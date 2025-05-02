# /home/ubuntu/ai_artist_system_clone/services/error_analysis_service.py
"""
Service for analyzing log files, identifying errors, attempting auto-fixing,
and logging results to the database.
"""

import logging
import os
import sys
import asyncio
import re
import time
import traceback
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# --- Import necessary components ---
try:
    from llm_orchestrator.orchestrator import LLMOrchestrator, LLMOrchestratorError
    from services.telegram_service import send_notification
    # Import DB functions for error reporting
    from services.artist_db_service import add_error_report, update_error_report_status
except ImportError as e:
    logging.basicConfig(level=logging.ERROR)
    logging.error(f"Failed to import core modules for ErrorAnalysisService: {e}")
    # Define dummy functions if imports fail to allow basic structure
    LLMOrchestrator = None
    LLMOrchestratorError = Exception
    async def send_notification(message: str):
        print(f"[Dummy Notify] {message}")
        await asyncio.sleep(0)
    def add_error_report(report_data: Dict[str, Any]) -> Optional[int]:
        print(f"[Dummy DB] Add Error Report: {report_data}")
        return 1 # Dummy ID
    def update_error_report_status(report_id: int, new_status: str, update_data: Optional[Dict[str, Any]] = None) -> bool:
        # Modified dummy to accept update_data
        print(f"[Dummy DB] Update Error Report {report_id}: Status={new_status}, Data={update_data}")
        return True

# --- Configuration ---
LOG_FILE_TO_MONITOR = os.path.join(PROJECT_ROOT, "logs", "batch_runner.log")
ERROR_ANALYSIS_LLM_PRIMARY = os.getenv("ERROR_ANALYSIS_LLM_PRIMARY", "deepseek:deepseek-chat")
ERROR_ANALYSIS_LLM_FALLBACKS = os.getenv("ERROR_ANALYSIS_LLM_FALLBACKS", "gemini:gemini-pro").split(",")
ERROR_ANALYSIS_MAX_TOKENS = int(os.getenv("ERROR_ANALYSIS_MAX_TOKENS", 1000))
ERROR_ANALYSIS_TEMPERATURE = float(os.getenv("ERROR_ANALYSIS_TEMPERATURE", 0.5))
ENGINEER_LLM_PRIMARY = os.getenv("ENGINEER_LLM_PRIMARY", "deepseek:deepseek-coder") # Use a coder model if available
ENGINEER_LLM_FALLBACKS = os.getenv("ENGINEER_LLM_FALLBACKS", "gemini:gemini-pro").split(",")
ENGINEER_MAX_TOKENS = int(os.getenv("ENGINEER_MAX_TOKENS", 1500))
ENGINEER_TEMPERATURE = float(os.getenv("ENGINEER_TEMPERATURE", 0.3))
AUTO_FIX_ENABLED = os.getenv("AUTO_FIX_ENABLED", "False").lower() == "true"
MONITOR_INTERVAL_SECONDS = int(os.getenv("MONITOR_INTERVAL_SECONDS", 60))
ERROR_CONTEXT_LINES = int(os.getenv("ERROR_CONTEXT_LINES", 20))
SERVICE_NAME = "error_analysis_service" # Name of this service for logging

# Configure logging for this service
logger = logging.getLogger(__name__)

class ErrorAnalysisService:
    """
    Monitors log files, analyzes errors using LLMs, logs to DB, and optionally attempts auto-fixing.
    """

    def __init__(self):
        self.last_check_time = datetime.utcnow() - timedelta(minutes=5) # Start check from 5 mins ago
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
                    enable_fallback_notifications=False # Avoid notification loops
                )
                logger.info("Log Analyzer LLM Orchestrator initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Log Analyzer LLM Orchestrator: {e}")

            try:
                self.llm_engineer = LLMOrchestrator(
                    primary_model=ENGINEER_LLM_PRIMARY,
                    fallback_models=ENGINEER_LLM_FALLBACKS,
                    enable_auto_discovery=False,
                    enable_fallback_notifications=False # Avoid notification loops
                )
                logger.info("Engineer LLM Orchestrator initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Engineer LLM Orchestrator: {e}")
        else:
            logger.error("LLM Orchestrator not available. Error analysis and fixing disabled.")

    async def monitor_log_file(self):
        """Periodically checks the log file for new error messages."""
        logger.info(f"Starting log monitor for {LOG_FILE_TO_MONITOR}")
        while True:
            try:
                await self.check_for_errors()
            except Exception as e:
                logger.error(f"Error during log monitoring cycle: {e}", exc_info=True)
                # Log monitoring failure to DB and notify
                error_report_id = add_error_report({
                    "timestamp": datetime.utcnow().isoformat(),
                    "error_log": f"Monitoring loop failed: {traceback.format_exc()}",
                    "status": "monitor_failed",
                    "service_name": SERVICE_NAME
                })
                await send_notification(f"🚨 Error Analysis Service Alert: Monitoring loop failed! Error: {e}. Report ID: {error_report_id}")
            await asyncio.sleep(MONITOR_INTERVAL_SECONDS)

    async def check_for_errors(self):
        """Checks the log file for errors since the last check."""
        if not os.path.exists(LOG_FILE_TO_MONITOR):
            logger.warning(f"Log file {LOG_FILE_TO_MONITOR} not found. Skipping check.")
            return

        current_check_time = datetime.utcnow()
        new_errors = []
        try:
            with open(LOG_FILE_TO_MONITOR, "r") as f:
                lines = f.readlines()

            error_block = []
            in_error_block = False
            timestamp_format = "%Y-%m-%d %H:%M:%S,%f"
            error_timestamp = None
            error_service = "unknown" # Try to infer service from log line

            for i, line in enumerate(lines):
                # Try to parse timestamp and service name
                try:
                    # Format: 2024-05-02 20:42:05,123 - service_name - LEVEL - message
                    parts = line.split(" - ", 3)
                    log_timestamp_str = parts[0]
                    log_timestamp = datetime.strptime(log_timestamp_str, timestamp_format)
                    if len(parts) > 2:
                        potential_service = parts[1]
                        # Basic check if it looks like a service name (avoid log levels)
                        if potential_service not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                             current_service = potential_service

                except (ValueError, IndexError):
                    # If parsing fails or line format is wrong, check if part of a traceback
                    if in_error_block and line.startswith((" ", "\t", "Traceback")):
                        error_block.append(line.strip())
                    else:
                        if in_error_block:
                            # End of traceback block
                            new_errors.append({
                                "log": "\n".join(error_block),
                                "timestamp": error_timestamp or self.last_check_time.isoformat(),
                                "service": error_service
                            })
                            error_block = []
                        in_error_block = False
                    continue # Skip lines without valid timestamp format at the start

                if log_timestamp > self.last_check_time:
                    if "ERROR" in line or "CRITICAL" in line:
                        if not in_error_block:
                            # Start of a new error block, include context lines before
                            start_context = max(0, i - ERROR_CONTEXT_LINES)
                            error_block.extend([l.strip() for l in lines[start_context:i]])
                            in_error_block = True
                            error_timestamp = log_timestamp.isoformat()
                            error_service = current_service # Capture service at error start
                        error_block.append(line.strip())
                    elif in_error_block and line.startswith((" ", "\t", "Traceback")):
                        # Part of a traceback for a recent error
                        error_block.append(line.strip())
                    elif in_error_block:
                        # End of error block
                        new_errors.append({
                            "log": "\n".join(error_block),
                            "timestamp": error_timestamp or self.last_check_time.isoformat(),
                            "service": error_service
                        })
                        error_block = []
                        in_error_block = False

            # Add the last block if file ends during it
            if in_error_block:
                 new_errors.append({
                    "log": "\n".join(error_block),
                    "timestamp": error_timestamp or self.last_check_time.isoformat(),
                    "service": error_service
                 })

        except Exception as e:
            logger.error(f"Error reading or parsing log file {LOG_FILE_TO_MONITOR}: {e}")
            # Log parsing failure to DB and notify
            error_report_id = add_error_report({
                "timestamp": datetime.utcnow().isoformat(),
                "error_log": f"Log file parsing failed: {traceback.format_exc()}",
                "status": "parse_failed",
                "service_name": SERVICE_NAME
            })
            await send_notification(f"🚨 Error Analysis Service Alert: Failed to read/parse log file {LOG_FILE_TO_MONITOR}. Error: {e}. Report ID: {error_report_id}")
            self.last_check_time = current_check_time
            return

        self.last_check_time = current_check_time

        if new_errors:
            logger.info(f"Found {len(new_errors)} new error block(s) in log file.")
            # Process the first significant new error to avoid spamming
            first_error = new_errors[0]
            error_log_content = first_error["log"]
            error_hash = str(hash(error_log_content)) # Use string hash

            if error_hash != self.last_error_hash:
                self.last_error_hash = error_hash
                self.error_count = 1
                # Add initial report to DB
                report_id = add_error_report({
                    "timestamp": first_error["timestamp"],
                    "error_hash": error_hash,
                    "error_log": error_log_content,
                    "status": "new",
                    "service_name": first_error["service"]
                })
                if report_id:
                    await self.analyze_and_fix_error(report_id, error_log_content)
                else:
                    logger.error("Failed to add initial error report to database. Aborting analysis.")
                    await send_notification(f"🚨 Error Analysis Service Alert: Failed to log new error (hash: {error_hash}) to DB. Manual check required.")
            else:
                self.error_count += 1
                logger.warning(f"Detected repeated error (hash: {error_hash}). Count: {self.error_count}. Skipping analysis.")
                if self.error_count % 5 == 0: # Notify every 5 repeats
                     await send_notification(f"⚠️ Error Analysis Service Alert: Repeated error detected {self.error_count} times (Hash: {error_hash}). Last error block:\n```\n{error_log_content[-1000:]}\n```")
        else:
             logger.debug("No new errors found in log file.")
             self.last_error_hash = None # Reset hash if no errors
             self.error_count = 0

    async def analyze_and_fix_error(self, report_id: int, error_log: str):
        """Analyzes the error log using LLM, logs to DB, and attempts to fix it."""
        logger.info(f"Analyzing detected error (Report ID: {report_id})...")
        await send_notification(f"🚨 Error Detected (Report ID: {report_id})! Analyzing...\n```\n{error_log[-1000:]} \n```") # Send last 1000 chars

        if not self.llm_analyzer or not self.llm_engineer:
            logger.error("LLM Orchestrators not available. Cannot analyze or fix error.")
            update_error_report_status(report_id, "analysis_failed", {"analysis": "LLM services unavailable"})
            await send_notification(f"🚨 Error Analysis Failed (Report ID: {report_id}): LLM services unavailable. Manual intervention required.")
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
                temperature=ERROR_ANALYSIS_TEMPERATURE
            )
            if not analysis_result:
                logger.error("LLM analysis returned empty result.")
                analysis_status = "analysis_failed"
                analysis_result = "LLM analysis returned empty."
            else:
                logger.info(f"LLM Analysis Result (Report ID: {report_id}): {analysis_result}")
                await send_notification(f"📊 Error Analysis Complete (Report ID: {report_id}):\n{analysis_result}")
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            analysis_status = "analysis_failed"
            analysis_result = f"LLM analysis step encountered an error: {e}"
            await send_notification(f"🚨 Error Analysis Failed (Report ID: {report_id}): {analysis_result}. Manual intervention required.")

        # Update DB with analysis result and status
        update_error_report_status(report_id, analysis_status, {"analysis": analysis_result})

        if analysis_status == "analysis_failed":
            return # Stop if analysis failed

        # 2. Generate Fix (if analysis successful)
        fix_suggestion = None
        fix_status = "fix_suggested"
        engineer_prompt = f"""
        Based on the following error log and analysis, generate a potential code patch in `diff` format to fix the issue.
        If a code patch is not feasible, suggest specific configuration changes or manual steps.
        Prioritize simple, targeted fixes.
        Ensure the patch applies cleanly to standard Python code.
        If suggesting code, provide ONLY the diff block starting with --- and +++ lines, including relative file paths (e.g., --- a/services/some_service.py).

        Error Log:
        ```
        {error_log}
        ```

        Analysis:
        ```
        {analysis_result}
        ```

        Suggested Fix (Diff format or steps):
        """
        try:
            fix_suggestion = await self.llm_engineer.generate(
                prompt=engineer_prompt,
                max_tokens=ENGINEER_MAX_TOKENS,
                temperature=ENGINEER_TEMPERATURE
            )
            if not fix_suggestion:
                logger.error("LLM fix generation returned empty result.")
                fix_status = "fix_failed"
                fix_suggestion = "LLM fix generation returned empty."
            else:
                logger.info(f"LLM Fix Suggestion (Report ID: {report_id}): {fix_suggestion}")
                # Assume diff format for notification, but log full suggestion
                await send_notification(f"🛠️ Potential Fix Suggested (Report ID: {report_id}):\n```diff\n{fix_suggestion}\n```")
        except Exception as e:
            logger.error(f"LLM fix generation failed: {e}")
            fix_status = "fix_failed"
            fix_suggestion = f"LLM engineer step encountered an error: {e}"
            await send_notification(f"🚨 Fix Generation Failed (Report ID: {report_id}): {fix_suggestion}. Manual intervention required.")

        # Update DB with fix suggestion and status
        update_error_report_status(report_id, fix_status, {"fix_suggestion": fix_suggestion})

        if fix_status == "fix_failed":
            return # Stop if fix generation failed

        # 3. Apply Fix (Optional)
        apply_status = "fix_skipped"
        if AUTO_FIX_ENABLED and fix_suggestion and "--- a/" in fix_suggestion and "+++ b/" in fix_suggestion:
            logger.info(f"Auto-fix enabled. Attempting to apply patch (Report ID: {report_id})...")
            apply_status = "fix_attempted"
            update_error_report_status(report_id, apply_status)
            success = await self.apply_git_patch(fix_suggestion)
            if success:
                apply_status = "fix_applied"
                logger.info(f"Auto-fix patch applied successfully (Report ID: {report_id}).")
                await send_notification(f"✅ Auto-Fix Applied Successfully (Report ID: {report_id})! Monitoring for recurrence.")
            else:
                apply_status = "fix_failed"
                logger.error(f"Auto-fix patch application failed (Report ID: {report_id}).")
                await send_notification(f"❌ Auto-Fix Failed (Report ID: {report_id}): Could not apply suggested patch. Manual intervention required.")
            # Update DB with final apply status
            update_error_report_status(report_id, apply_status)
        elif AUTO_FIX_ENABLED:
             apply_status = "fix_skipped_invalid"
             logger.warning(f"Auto-fix enabled, but suggestion is not a valid diff patch (Report ID: {report_id}). Manual intervention required.")
             await send_notification(f"⚠️ Auto-Fix Skipped (Report ID: {report_id}): Suggestion is not a diff patch. Manual intervention required.")
             update_error_report_status(report_id, apply_status)
        else:
            logger.info(f"Auto-fix disabled (Report ID: {report_id}). Manual intervention required to apply the fix.")
            # Status remains 'fix_suggested' or 'fix_failed' from previous step

    async def apply_git_patch(self, patch_content: str) -> bool:
        """Applies a patch using git apply. Assumes running in the repo root."""
        # Caution: This is a simplified example. Real implementation needs robust error handling,
        # path validation, and potentially running in a specific directory.
        patch_file = os.path.join(PROJECT_ROOT, "temp_fix.patch")
        try:
            # Ensure patch content ends with a newline for git apply
            if not patch_content.endswith('\n'):
                patch_content += '\n'

            with open(patch_file, "w") as f:
                f.write(patch_content)

            # Run git apply --check first
            proc_check = await asyncio.create_subprocess_shell(
                f"git apply --check --verbose {patch_file}", # Add verbose for more info
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=PROJECT_ROOT
            )
            stdout_check, stderr_check = await proc_check.communicate()
            logger.debug(f"git apply --check stdout:\n{stdout_check.decode()}")

            if proc_check.returncode != 0:
                logger.error(f"git apply --check failed:\n{stderr_check.decode()}")
                return False
            else:
                 logger.info("git apply --check successful.")

            # Apply the patch
            proc_apply = await asyncio.create_subprocess_shell(
                f"git apply --verbose {patch_file}", # Add verbose
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=PROJECT_ROOT
            )
            stdout_apply, stderr_apply = await proc_apply.communicate()
            logger.debug(f"git apply stdout:\n{stdout_apply.decode()}")

            if proc_apply.returncode == 0:
                logger.info("git apply successful.")
                return True
            else:
                logger.error(f"git apply failed:\n{stderr_apply.decode()}")
                # Attempt to reverse if apply failed mid-way (best effort)
                logger.warning("Attempting to reverse failed patch application...")
                proc_reverse = await asyncio.create_subprocess_shell(
                    f"git apply --reverse {patch_file}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=PROJECT_ROOT
                )
                await proc_reverse.communicate()
                logger.warning(f"Reversal attempt finished with code {proc_reverse.returncode}")
                return False
        except Exception as e:
            logger.error(f"Error applying git patch: {e}", exc_info=True)
            return False
        finally:
            # Clean up patch file
            if os.path.exists(patch_file):
                try:
                    os.remove(patch_file)
                except OSError as e:
                    logger.error(f"Failed to remove temporary patch file {patch_file}: {e}")

# --- Main Execution (for running as a separate service) ---
async def main():
    # Ensure DB is initialized before starting monitor
    from services.artist_db_service import initialize_database
    initialize_database()

    service = ErrorAnalysisService()
    await service.monitor_log_file()

if __name__ == "__main__":
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)] # Log to stdout when run directly
    )
    logger.info("Starting Error Analysis Service...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Error Analysis Service stopped by user.")

