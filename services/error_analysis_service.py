# /home/ubuntu/ai_artist_system_clone/services/error_analysis_service.py
"""
Service for analyzing log files, identifying errors, attempting auto-fixing, and logging results to the database.
"""

import logging
import os
import sys
import asyncio
import traceback
import tempfile  # Added import
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# --- Import necessary components ---
try:
    from llm_orchestrator.orchestrator import (
        LLMOrchestrator,
        LLMOrchestratorError,
    )
    from services.telegram_service import send_notification

    # Import DB functions for error reporting
    from services.artist_db_service import (
        add_error_report,
        update_error_report_status,
    )

    db_imports_successful = True  # Added flag
except ImportError as e:
    logging.basicConfig(level=logging.ERROR)
    logging.error(
        f"Failed to import core modules for ErrorAnalysisService: {e}"
    )
    # Define dummy functions if imports fail to allow basic structure
    LLMOrchestrator = None
    LLMOrchestratorError = Exception
    db_imports_successful = False  # Added flag

    async def send_notification(message: str):
        print(f"[Dummy Notify] {message}")
        await asyncio.sleep(0)

    def add_error_report(report_data: Dict[str, Any]) -> Optional[int]:
        print(f"[Dummy DB] Add Error Report: {report_data}")
        return 1  # Dummy ID

    def update_error_report_status(
        report_id: int,
        new_status: str,
        update_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # Modified dummy to accept update_data
        print(
            f"[Dummy DB] Update Error Report {report_id}: Status={new_status}, Data={update_data}"
        )
        return True


# --- Configuration ---
LOG_FILE_TO_MONITOR = os.path.join(PROJECT_ROOT, "logs", "batch_runner.log")
ERROR_ANALYSIS_LLM_PRIMARY = os.getenv(
    "ERROR_ANALYSIS_LLM_PRIMARY", "deepseek:deepseek-chat"
)
ERROR_ANALYSIS_LLM_FALLBACKS = os.getenv(
    "ERROR_ANALYSIS_LLM_FALLBACKS", "gemini:gemini-pro"
).split(",")
ERROR_ANALYSIS_MAX_TOKENS = int(os.getenv("ERROR_ANALYSIS_MAX_TOKENS", 1000))
ERROR_ANALYSIS_TEMPERATURE = float(
    os.getenv("ERROR_ANALYSIS_TEMPERATURE", 0.5)
)
ENGINEER_LLM_PRIMARY = os.getenv(
    "ENGINEER_LLM_PRIMARY", "deepseek:deepseek-coder"
)  # Use a coder model if available
ENGINEER_LLM_FALLBACKS = os.getenv(
    "ENGINEER_LLM_FALLBACKS", "gemini:gemini-pro"
).split(",")
ENGINEER_MAX_TOKENS = int(os.getenv("ENGINEER_MAX_TOKENS", 1500))
ENGINEER_TEMPERATURE = float(os.getenv("ENGINEER_TEMPERATURE", 0.3))
AUTO_FIX_ENABLED = os.getenv("AUTO_FIX_ENABLED", "False").lower() == "true"
MONITOR_INTERVAL_SECONDS = int(os.getenv("MONITOR_INTERVAL_SECONDS", 60))
ERROR_CONTEXT_LINES = int(os.getenv("ERROR_CONTEXT_LINES", 20))
SERVICE_NAME = "error_analysis_service"  # Name of this service for logging

# Configure logging for this service
logger = logging.getLogger(__name__)


class ErrorAnalysisService:
    """
    Monitors log files, analyzes errors using LLMs, logs to DB, and optionally attempts auto-fixing.
    """

    def __init__(self):
        self.last_check_time = datetime.utcnow() - timedelta(
            minutes=5
        )  # Start check from 5 mins ago
        self.last_error_hash = None
        self.error_count = 0
        self.llm_analyzer = None
        self.llm_engineer = None

        if LLMOrchestrator:
            try:
                self.llm_analyzer = LLMOrchestrator(
                    primary_model=ERROR_ANALYSIS_LLM_PRIMARY,
                    fallback_models=ERROR_ANALYSIS_LLM_FALLBACKS,
                    enable_auto_discovery=False,
                    enable_fallback_notifications=False,  # Avoid notification loops
                )
                logger.info("Log Analyzer LLM Orchestrator initialized.")
            except Exception as e:
                logger.error(
                    f"Failed to initialize Log Analyzer LLM Orchestrator: {e}"
                )

            try:
                self.llm_engineer = LLMOrchestrator(
                    primary_model=ENGINEER_LLM_PRIMARY,
                    fallback_models=ENGINEER_LLM_FALLBACKS,
                    enable_auto_discovery=False,
                    enable_fallback_notifications=False,  # Avoid notification loops
                )
                logger.info("Engineer LLM Orchestrator initialized.")
            except Exception as e:
                logger.error(
                    f"Failed to initialize Engineer LLM Orchestrator: {e}"
                )
        else:
            logger.error(
                "LLM Orchestrator not available. Error analysis and fixing disabled."
            )

    async def monitor_log_file(self):
        """Periodically checks the log file for new error messages."""
        logger.info(f"Starting log monitor for {LOG_FILE_TO_MONITOR}")
        while True:
            try:
                await self.check_for_errors()
            except Exception as e:
                logger.error(
                    f"Error during log monitoring cycle: {e}", exc_info=True
                )
                # Log monitoring failure to DB and notify
                if db_imports_successful:  # Check if DB functions available
                    error_report_id = add_error_report(
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "error_log": f"Monitoring loop failed: {traceback.format_exc()}",
                            "status": "monitor_failed",
                            "service_name": SERVICE_NAME,
                        }
                    )
                    await send_notification(
                        f"🚨 Error Analysis Service Alert: Monitoring loop failed! Error: {e}. Report ID: {error_report_id}"
                    )
                else:
                    await send_notification(
                        f"🚨 Error Analysis Service Alert: Monitoring loop failed! Error: {e}. DB logging unavailable."
                    )

            await asyncio.sleep(MONITOR_INTERVAL_SECONDS)

    async def check_for_errors(self):
        """Checks the log file for errors since the last check."""
        if not os.path.exists(LOG_FILE_TO_MONITOR):
            logger.warning(
                f"Log file {LOG_FILE_TO_MONITOR} not found. Skipping check."
            )
            return

        current_check_time = datetime.utcnow()
        new_errors = []
        current_service = "unknown"  # Track current service context

        try:
            with open(LOG_FILE_TO_MONITOR, "r") as f:
                lines = f.readlines()

            error_block = []
            in_error_block = False
            timestamp_format = "%Y-%m-%d %H:%M:%S,%f"
            error_timestamp = None
            error_service = "unknown"  # Try to infer service from log line

            for i, line in enumerate(lines):
                # Try to parse timestamp and service name
                try:
                    # Format: 2024-05-02 20:42:05,123 - service_name - LEVEL - message
                    parts = line.split(" - ", 3)
                    log_timestamp_str = parts[0]
                    log_timestamp = datetime.strptime(
                        log_timestamp_str, timestamp_format
                    )
                    if len(parts) > 2:
                        potential_service = parts[1]
                        # Basic check if it looks like a service name (avoid log levels)
                        if potential_service not in [
                            "DEBUG",
                            "INFO",
                            "WARNING",
                            "ERROR",
                            "CRITICAL",
                        ]:
                            current_service = potential_service  # Update current service context

                except (ValueError, IndexError):
                    # If parsing fails or line format is wrong, check if part of a traceback
                    if in_error_block and line.startswith(
                        (" ", "\t", "Traceback")
                    ):
                        error_block.append(line.strip())
                    else:
                        if in_error_block:
                            # End of traceback block
                            new_errors.append(
                                {
                                    "log": "\n".join(error_block),
                                    "timestamp": error_timestamp
                                    or self.last_check_time.isoformat(),
                                    "service": error_service,
                                }
                            )
                            error_block = []
                        in_error_block = False
                    continue  # Skip lines without valid timestamp format at the start

                if log_timestamp > self.last_check_time:
                    if "ERROR" in line or "CRITICAL" in line:
                        if not in_error_block:
                            # Start of a new error block, include context lines before
                            start_context = max(0, i - ERROR_CONTEXT_LINES)
                            error_block.extend(
                                [
                                    log_line.strip()
                                    for log_line in lines[start_context:i]
                                ]
                            )
                            in_error_block = True
                            error_timestamp = log_timestamp.isoformat()
                            error_service = current_service  # Capture service at error start
                        error_block.append(line.strip())
                    elif in_error_block and line.startswith(
                        (" ", "\t", "Traceback")
                    ):
                        # Part of a traceback for a recent error
                        error_block.append(line.strip())
                    elif in_error_block:
                        # End of error block
                        new_errors.append(
                            {
                                "log": "\n".join(error_block),
                                "timestamp": error_timestamp
                                or self.last_check_time.isoformat(),
                                "service": error_service,
                            }
                        )
                        error_block = []
                        in_error_block = False

            # Add the last block if file ends during it
            if in_error_block:
                new_errors.append(
                    {
                        "log": "\n".join(error_block),
                        "timestamp": error_timestamp
                        or self.last_check_time.isoformat(),
                        "service": error_service,
                    }
                )

        except Exception as e:
            logger.error(
                f"Error reading or parsing log file {LOG_FILE_TO_MONITOR}: {e}"
            )
            # Log parsing failure to DB and notify
            if db_imports_successful:
                error_report_id = add_error_report(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "error_log": f"Log file parsing failed: {traceback.format_exc()}",
                        "status": "parse_failed",
                        "service_name": SERVICE_NAME,
                    }
                )
                await send_notification(
                    f"🚨 Error Analysis Service Alert: Failed to read/parse log file {LOG_FILE_TO_MONITOR}. Error: {e}. Report ID: {error_report_id}"
                )
            else:
                await send_notification(
                    f"🚨 Error Analysis Service Alert: Failed to read/parse log file {LOG_FILE_TO_MONITOR}. Error: {e}. DB logging unavailable."
                )
            self.last_check_time = current_check_time
            return

        self.last_check_time = current_check_time

        if new_errors:
            logger.info(
                f"Found {len(new_errors)} new error block(s) in log file."
            )
            # Process the first significant new error to avoid spamming
            first_error = new_errors[0]
            error_log_content = first_error["log"]
            error_hash = str(hash(error_log_content))  # Use string hash

            if error_hash != self.last_error_hash:
                self.last_error_hash = error_hash
                self.error_count = 1
                # Add initial report to DB
                report_id = None
                if db_imports_successful:
                    report_id = add_error_report(
                        {
                            "timestamp": first_error["timestamp"],
                            "error_hash": error_hash,
                            "error_log": error_log_content,
                            "status": "new",
                            "service_name": first_error["service"],
                        }
                    )

                if report_id:
                    await self.analyze_and_fix_error(
                        report_id, error_log_content
                    )
                else:
                    # Log locally and notify if DB add failed or unavailable
                    logger.error(
                        "Failed to add initial error report to database. Aborting analysis."
                    )
                    await send_notification(
                        f"🚨 Error Analysis Service Alert: Failed to log new error (hash: {error_hash}) to DB. Manual check required."
                    )
            else:
                self.error_count += 1
                logger.warning(
                    f"Detected repeated error (hash: {error_hash}). Count: {self.error_count}. Skipping analysis."
                )
                if self.error_count % 5 == 0:  # Notify every 5 repeats
                    await send_notification(
                        f"⚠️ Error Analysis Service Alert: Repeated error detected {self.error_count} times (Hash: {error_hash}). Last error block:\n```\n{error_log_content[-1000:]}\n```"
                    )
        else:
            logger.debug("No new errors found in log file.")
            self.last_error_hash = None  # Reset hash if no errors
            self.error_count = 0

    async def analyze_and_fix_error(self, report_id: int, error_log: str):
        """Analyzes the error log using LLM, logs to DB, and attempts to fix it."""
        logger.info(f"Analyzing detected error (Report ID: {report_id})...")
        await send_notification(
            f"🚨 Error Detected (Report ID: {report_id})! Analyzing...\n```\n{error_log[-1000:]} \n```"
        )  # Send last 1000 chars

        if not self.llm_analyzer or not self.llm_engineer:
            logger.error(
                "LLM Orchestrators not available. Cannot analyze or fix error."
            )
            if db_imports_successful:
                update_error_report_status(
                    report_id,
                    "analysis_failed",
                    {"analysis": "LLM services unavailable"},
                )
            await send_notification(
                f"🚨 Error Analysis Failed (Report ID: {report_id}): LLM services unavailable. Manual intervention required."
            )
            return

        # 1. Analyze Error
        analysis_result = None
        analysis_status = "analyzed"
        analysis_prompt = f"""
        Analyze the following error log from a Python application (AI Artist System).
        Identify the root cause, the affected module/function, and suggest a general approach to fix it.
        Focus on actionable insights.

        Error Log:
        ```
        {error_log}
        ```

        Analysis:
        """
        try:
            analysis_result = await self.llm_analyzer.generate(
                prompt=analysis_prompt,
                max_tokens=ERROR_ANALYSIS_MAX_TOKENS,
                temperature=ERROR_ANALYSIS_TEMPERATURE,
            )
            if not analysis_result:
                logger.error("LLM analysis returned empty result.")
                analysis_status = "analysis_failed"
                analysis_result = "LLM analysis returned empty result."
        except LLMOrchestratorError as e:
            logger.error(f"LLM analysis failed: {e}")
            analysis_status = "analysis_failed"
            analysis_result = f"LLM analysis failed: {e}"
        except Exception as e:
            logger.error(
                f"Unexpected error during LLM analysis: {e}", exc_info=True
            )
            analysis_status = "analysis_failed"
            analysis_result = f"Unexpected error during analysis: {e}"

        # Log analysis result
        if db_imports_successful:
            update_error_report_status(
                report_id, analysis_status, {"analysis": analysis_result}
            )

        if analysis_status == "analysis_failed":
            await send_notification(
                f"🚨 Error Analysis Failed (Report ID: {report_id}): {analysis_result}. Manual intervention required."
            )
            return

        logger.info(
            f"Error analysis complete (Report ID: {report_id}). Result:\n{analysis_result}"
        )
        await send_notification(
            f"ℹ️ Error Analysis Complete (Report ID: {report_id}). Analysis:\n{analysis_result}"
        )

        # 2. Attempt Auto-Fix (if enabled and analysis successful)
        if AUTO_FIX_ENABLED and analysis_status == "analyzed":
            logger.info(
                f"Attempting auto-fix for error (Report ID: {report_id})..."
            )
            fix_status = "fix_attempted"
            fix_details = ""

            # Extract relevant file path from error log (simple approach)
            file_path_match = next(
                (line for line in error_log.splitlines() if 'File "' in line),
                None,
            )
            target_file = None
            if file_path_match:
                try:
                    # Extract path between quotes
                    target_file = file_path_match.split('"')[1]
                    # Make path absolute if relative to project root
                    if not os.path.isabs(target_file) and PROJECT_ROOT:
                        potential_path = os.path.join(
                            PROJECT_ROOT, target_file
                        )
                        if os.path.exists(potential_path):
                            target_file = potential_path
                        else:
                            logger.warning(
                                f"Could not resolve relative path: {target_file}"
                            )
                            target_file = None  # Reset if path invalid
                except IndexError:
                    logger.warning(
                        "Could not parse file path from error log line."
                    )

            if not target_file or not os.path.exists(target_file):
                fix_status = "fix_failed"
                fix_details = "Could not identify or find the affected file from the error log."
                logger.error(fix_details)
            else:
                logger.info(
                    f"Identified target file for patching: {target_file}"
                )
                try:
                    with open(target_file, "r") as f:
                        file_content = f.read()

                    fix_prompt = f"""
                    Given the following Python code from file '{target_file}' and the error log analysis, generate a patch in standard diff format (`diff -u`) to fix the error.
                    Only output the patch content, nothing else.

                    File Content (`{target_file}`):
                    ```python
                    {file_content}
                    ```

                    Error Log:
                    ```
                    {error_log}
                    ```

                    Error Analysis:
                    ```
                    {analysis_result}
                    ```

                    Patch:
                    """
                    patch_content = await self.llm_engineer.generate(
                        prompt=fix_prompt,
                        max_tokens=ENGINEER_MAX_TOKENS,
                        temperature=ENGINEER_TEMPERATURE,
                    )

                    if (
                        not patch_content
                        or not patch_content.strip().startswith(
                            ("--- ", "+++ ")
                        )
                    ):
                        fix_status = "fix_failed"
                        fix_details = "LLM did not generate a valid patch."
                        logger.error(
                            f"{fix_details} Raw output: {patch_content}"
                        )
                    else:
                        logger.info(f"Generated patch:\n{patch_content}")
                        fix_details = (
                            patch_content  # Store the generated patch
                        )
                        # Apply the patch
                        patch_applied = await self._apply_patch(
                            report_id, patch_content
                        )
                        if patch_applied:
                            fix_status = "fix_applied"
                            logger.info("Auto-fix patch applied successfully.")
                            await send_notification(
                                f"✅ Auto-fix Applied (Report ID: {report_id})! Patch applied successfully."
                            )
                        else:
                            fix_status = "fix_failed"
                            # Details already logged in _apply_patch
                            logger.error("Auto-fix patch application failed.")
                            # Notification sent by _apply_patch on failure

                except FileNotFoundError:
                    fix_status = "fix_failed"
                    fix_details = f"Target file {target_file} not found during fix attempt."
                    logger.error(fix_details)
                except LLMOrchestratorError as e:
                    fix_status = "fix_failed"
                    fix_details = f"LLM patch generation failed: {e}"
                    logger.error(fix_details)
                except Exception as e:
                    fix_status = "fix_failed"
                    fix_details = (
                        f"Unexpected error during auto-fix attempt: {e}"
                    )
                    logger.error(fix_details, exc_info=True)

            # Update DB with fix status
            if db_imports_successful:
                update_error_report_status(
                    report_id, fix_status, {"fix_details": fix_details}
                )
            if fix_status == "fix_failed":
                await send_notification(
                    f"❌ Auto-fix Failed (Report ID: {report_id}): {fix_details}. Manual intervention required."
                )

        elif not AUTO_FIX_ENABLED:
            logger.info("Auto-fix is disabled. Skipping fix attempt.")
            if db_imports_successful:
                update_error_report_status(report_id, "fix_skipped_disabled")
        else:  # analysis failed previously
            logger.info("Skipping fix attempt due to failed analysis.")
            # Status already updated during analysis failure

    async def _apply_patch(self, report_id: int, patch_content: str) -> bool:
        """Applies the generated patch using git apply."""
        patch_file = None
        try:
            # Create a temporary file for the patch
            with tempfile.NamedTemporaryFile(
                mode="w",
                delete=False,
                suffix=".patch",
                prefix=f"errorfix_{report_id}_",
            ) as f:
                patch_file = f.name
                f.write(patch_content)
            logger.debug(
                f"Patch content written to temporary file: {patch_file}"
            )

            # --- Corrected Block Start ---
            # Run git apply --check first
            logger.debug(f"Running git apply --check --verbose {patch_file}")
            proc_check = await asyncio.create_subprocess_shell(
                # Add verbose for more info
                f"git apply --check --verbose {patch_file}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=PROJECT_ROOT,  # Ensure command runs in the correct directory
            )
            stdout_check, stderr_check = await proc_check.communicate()

            # Log stdout and stderr for debugging
            stdout_decoded = stdout_check.decode().strip()
            stderr_decoded = stderr_check.decode().strip()
            if stdout_decoded:
                logger.debug(f"git apply --check stdout:\n{stdout_decoded}")
            if stderr_decoded:
                # Stderr might contain warnings even on success, log as debug/info
                logger.debug(f"git apply --check stderr:\n{stderr_decoded}")

            if proc_check.returncode != 0:
                logger.error(
                    f"git apply --check failed with return code {proc_check.returncode}."
                )
                # Log stderr specifically on failure
                if stderr_decoded:
                    logger.error(f"Error details:\n{stderr_decoded}")
                # Update DB status for check failure
                if db_imports_successful:
                    update_error_report_status(
                        report_id,
                        "fix_failed",
                        {
                            "fix_details": f"git apply --check failed: {stderr_decoded}"
                        },
                    )
                await send_notification(
                    f"❌ Auto-fix Failed (Report ID: {report_id}): git apply --check command failed."
                )
                return False
            else:
                logger.info("git apply --check passed successfully.")
            # --- Corrected Block End ---

            # If check passes, apply the patch
            logger.info(f"Applying patch from {patch_file}...")
            proc_apply = await asyncio.create_subprocess_shell(
                f"git apply {patch_file}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=PROJECT_ROOT,  # Ensure command runs in the correct directory
            )
            stdout_apply, stderr_apply = await proc_apply.communicate()

            if proc_apply.returncode == 0:
                logger.info("Patch applied successfully.")
                # Log stdout/stderr from apply as debug info
                if stdout_apply:
                    logger.debug(
                        f"git apply stdout:\n{stdout_apply.decode().strip()}"
                    )
                if stderr_apply:
                    logger.debug(
                        f"git apply stderr:\n{stderr_apply.decode().strip()}"
                    )
                return True  # Success
            else:
                apply_stderr_decoded = stderr_apply.decode().strip()
                logger.error(
                    f"git apply failed with return code {proc_apply.returncode}."
                )
                if apply_stderr_decoded:
                    logger.error(f"Error details:\n{apply_stderr_decoded}")

                # Log failure details to DB
                if db_imports_successful:
                    update_error_report_status(
                        report_id,
                        "fix_failed",
                        {
                            "fix_details": f"git apply failed: {apply_stderr_decoded}"
                        },
                    )
                await send_notification(
                    f"❌ Auto-fix Failed (Report ID: {report_id}): git apply command failed."
                )
                return False

        except Exception as e:
            logger.error(f"Error during patch application: {e}", exc_info=True)
            if db_imports_successful:
                update_error_report_status(
                    report_id,
                    "fix_failed",
                    {
                        "fix_details": f"Exception during patch application: {e}"
                    },
                )
            await send_notification(
                f"❌ Auto-fix Failed (Report ID: {report_id}): Exception during patch application."
            )
            return False
        finally:
            # Ensure patch file is removed
            if patch_file and os.path.exists(patch_file):
                try:
                    os.remove(patch_file)
                    logger.debug(f"Removed temporary patch file: {patch_file}")
                except OSError as e:
                    logger.warning(
                        f"Failed to remove patch file {patch_file} in finally block: {e}"
                    )


# --- Main Execution / Service Runner ---
async def main():
    # Basic logging config if not already set
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("Initializing Error Analysis Service...")
    service = ErrorAnalysisService()
    await service.monitor_log_file()  # Start the monitoring loop


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Error Analysis Service stopped by user.")
    except Exception as e:
        logger.critical(f"Error Analysis Service crashed: {e}", exc_info=True)
