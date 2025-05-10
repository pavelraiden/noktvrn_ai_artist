"""
Test cases for the LLM Orchestrator module.

This module contains test cases to validate the functionality of the
orchestrator, llm_interface, and session_manager modules.
"""

from llm_orchestrator.session_manager import (
    Session,
    SessionStatus,
    SessionManager,
)
from llm_orchestrator.orchestrator import (
    Orchestrator,
    OrchestrationResult,
    OrchestrationStatus,
    OrchestratorFactory,
)
from llm_orchestrator.llm_interface import (
    LLMRequest,
    LLMResponse,
    LLMRequestType,
    LLMProviderFactory,
    MockLLMProvider,
    SmartMockLLMProvider,
)
import sys
import os
import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path to import the modules
sys.path.append(str(Path(__file__).parent.parent))


class TestLLMInterface(unittest.TestCase):
    """Test cases for the LLM Interface module."""

    def test_llm_request_serialization(self):
        """Test LLMRequest serialization and deserialization."""
        # Create a request
        request = LLMRequest(
            request_type=LLMRequestType.GENERATE,
            prompt="Test prompt",
            parameters={"temperature": 0.7},
        )

        # Convert to dict
        request_dict = request.to_dict()

        # Convert back to request
        recreated_request = LLMRequest.from_dict(request_dict)

        # Check that the recreated request matches the original
        self.assertEqual(recreated_request.id, request.id)
        self.assertEqual(recreated_request.type, request.type)
        self.assertEqual(recreated_request.prompt, request.prompt)
        self.assertEqual(recreated_request.parameters, request.parameters)
        self.assertEqual(recreated_request.timestamp, request.timestamp)

    def test_llm_response_serialization(self):
        """Test LLMResponse serialization and deserialization."""
        # Create a response
        response = LLMResponse(
            request_id="test_request_id",
            content="Test content",
            metadata={"token_count": 10},
            latency=0.5,
        )

        # Convert to dict
        response_dict = response.to_dict()

        # Convert back to response
        recreated_response = LLMResponse.from_dict(response_dict)

        # Check that the recreated response matches the original
        self.assertEqual(recreated_response.request_id, response.request_id)
        self.assertEqual(recreated_response.content, response.content)
        self.assertEqual(recreated_response.metadata, response.metadata)
        self.assertEqual(recreated_response.latency, response.latency)
        self.assertEqual(recreated_response.timestamp, response.timestamp)

    async def test_mock_llm_provider(self):
        """Test MockLLMProvider functionality."""
        # Create a provider
        provider = MockLLMProvider()

        # Create a request
        request = LLMRequest(
            request_type=LLMRequestType.GENERATE,
            prompt="Test prompt",
            parameters={"temperature": 0.7},
        )

        # Send the request
        response = await provider.send_request(request)

        # Check the response
        self.assertEqual(response.request_id, request.id)
        self.assertTrue(response.content)
        self.assertIn("provider", response.metadata)
        self.assertIn("model", response.metadata)
        self.assertIn("token_count", response.metadata)
        self.assertGreaterEqual(response.latency, 0.0)

    async def test_smart_mock_llm_provider(self):
        """Test SmartMockLLMProvider functionality."""
        # Create a provider
        provider = SmartMockLLMProvider()

        # Create a request with session ID
        request = LLMRequest(
            request_type=LLMRequestType.GENERATE,
            prompt="Test prompt",
            parameters={"session_id": "test_session"},
        )

        # Send the request multiple times
        responses = []
        for _ in range(3):
            response = await provider.send_request(request)
            responses.append(response)

        # Check that the responses have increasing iteration counts
        for i, response in enumerate(responses):
            self.assertEqual(response.metadata["iteration"], i + 1)

    def test_llm_provider_factory(self):
        """Test LLMProviderFactory functionality."""
        # Create a mock provider
        mock_provider = LLMProviderFactory.create_provider("mock")
        self.assertIsInstance(mock_provider, MockLLMProvider)

        # Create a smart mock provider
        smart_mock_provider = LLMProviderFactory.create_provider("smart_mock")
        self.assertIsInstance(smart_mock_provider, SmartMockLLMProvider)

        # Create a provider with custom config
        custom_provider = LLMProviderFactory.create_provider(
            "mock",
            {
                "provider_name": "CustomMock",
                "model_name": "custom-model-v1",
                "latency_range": (0.1, 0.2),
                "error_rate": 0.1,
            },
        )
        self.assertEqual(custom_provider.provider_name, "CustomMock")
        self.assertEqual(custom_provider.model_name, "custom-model-v1")
        self.assertEqual(custom_provider.latency_range, (0.1, 0.2))
        self.assertEqual(custom_provider.error_rate, 0.1)

        # Test invalid provider type
        with self.assertRaises(ValueError):
            LLMProviderFactory.create_provider("invalid_provider")


class TestOrchestrator(unittest.TestCase):
    """Test cases for the Orchestrator module."""

    def test_orchestration_result_serialization(self):
        """Test OrchestrationResult serialization and deserialization."""
        # Create a result
        result = OrchestrationResult("test_orchestration_id")
        result.status = OrchestrationStatus.COMPLETED
        result.content = "Test content"
        result.iterations = 3
        result.confidence_score = 0.8
        result.add_to_history("generate", {"test": "data"})

        # Convert to dict
        result_dict = result.to_dict()

        # Convert back to result
        recreated_result = OrchestrationResult.from_dict(result_dict)

        # Check that the recreated result matches the original
        self.assertEqual(recreated_result.id, result.id)
        self.assertEqual(recreated_result.status, result.status)
        self.assertEqual(recreated_result.content, result.content)
        self.assertEqual(recreated_result.iterations, result.iterations)
        self.assertEqual(
            recreated_result.confidence_score, result.confidence_score
        )
        self.assertEqual(len(recreated_result.history), len(result.history))
        self.assertEqual(
            recreated_result.history[0]["type"], result.history[0]["type"]
        )

    async def test_orchestrator_factory(self):
        """Test OrchestratorFactory functionality."""
        # Create a default orchestrator
        orchestrator = OrchestratorFactory.create_default_orchestrator()
        self.assertIsInstance(orchestrator, Orchestrator)

        # Create an orchestrator from config
        config = {
            "generator": {
                "provider_type": "mock",
                "provider_config": {
                    "provider_name": "ConfigGenerator",
                    "model_name": "config-generator-v1",
                },
            },
            "reviewer": {
                "provider_type": "mock",
                "provider_config": {
                    "provider_name": "ConfigReviewer",
                    "model_name": "config-reviewer-v1",
                },
            },
            "refiner": {
                "provider_type": "mock",
                "provider_config": {
                    "provider_name": "ConfigRefiner",
                    "model_name": "config-refiner-v1",
                },
            },
            "confidence_threshold": 0.8,
            "max_iterations": 3,
        }

        orchestrator = OrchestratorFactory.create_orchestrator_from_config(
            config
        )
        self.assertIsInstance(orchestrator, Orchestrator)
        self.assertEqual(orchestrator.confidence_threshold, 0.8)
        self.assertEqual(orchestrator.max_iterations, 3)

    async def test_orchestrate_prompt(self):
        """Test orchestrating a prompt."""
        # Create an orchestrator with a high confidence threshold to ensure
        # multiple iterations
        orchestrator = OrchestratorFactory.create_default_orchestrator(
            confidence_threshold=0.95, max_iterations=3
        )

        # Define a prompt
        prompt = "Create a dark trap artist with mysterious vibes"

        # Orchestrate the prompt
        result = await orchestrator.orchestrate_prompt(prompt)

        # Check the result
        self.assertEqual(result.status, OrchestrationStatus.COMPLETED)
        self.assertIsNotNone(result.content)
        self.assertIsNotNone(result.confidence_score)
        self.assertLessEqual(result.iterations, 3)

        # Check history
        self.assertGreaterEqual(
            len(result.history), result.iterations * 2
        )  # At least 2 entries per iteration

        # Check that the history contains generate, review, and refine entries
        history_types = [entry["type"] for entry in result.history]
        self.assertIn("generate", history_types)
        self.assertIn("review", history_types)

        # If more than one iteration, should have refine entries
        if result.iterations > 1:
            self.assertIn("refine", history_types)


class TestSessionManager(unittest.TestCase):
    """Test cases for the Session Manager module."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for session storage
        self.temp_dir = tempfile.mkdtemp()
        self.session_manager = SessionManager(storage_dir=self.temp_dir)

    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_session_serialization(self):
        """Test Session serialization and deserialization."""
        # Create a session
        session = Session("test_session_id")

        # Add an orchestration
        orchestration = OrchestrationResult("test_orchestration_id")
        orchestration.status = OrchestrationStatus.COMPLETED
        orchestration.content = "Test content"
        session.add_orchestration(orchestration)

        # Convert to dict
        session_dict = session.to_dict()

        # Convert back to session
        recreated_session = Session.from_dict(session_dict)

        # Check that the recreated session matches the original
        self.assertEqual(recreated_session.id, session.id)
        self.assertEqual(recreated_session.status, session.status)
        self.assertEqual(
            len(recreated_session.orchestrations), len(session.orchestrations)
        )
        self.assertEqual(
            recreated_session.orchestrations["test_orchestration_id"].id,
            session.orchestrations["test_orchestration_id"].id,
        )

    def test_create_session(self):
        """Test creating a session."""
        # Create a session
        session = self.session_manager.create_session(
            metadata={"user_id": "test_user"}
        )

        # Check the session
        self.assertIsNotNone(session)
        self.assertEqual(session.status, SessionStatus.ACTIVE)
        self.assertEqual(session.metadata["user_id"], "test_user")

        # Check that the session was saved
        session_path = os.path.join(self.temp_dir, f"{session.id}.json")
        self.assertTrue(os.path.exists(session_path))

    def test_get_session(self):
        """Test getting a session."""
        # Create a session
        session = self.session_manager.create_session()

        # Get the session
        retrieved_session = self.session_manager.get_session(session.id)

        # Check the retrieved session
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.id, session.id)

        # Try to get a non-existent session
        non_existent_session = self.session_manager.get_session(
            "non_existent_id"
        )
        self.assertIsNone(non_existent_session)

    def test_add_orchestration_to_session(self):
        """Test adding an orchestration to a session."""
        # Create a session
        session = self.session_manager.create_session()

        # Create an orchestration
        orchestration = OrchestrationResult("test_orchestration_id")
        orchestration.status = OrchestrationStatus.COMPLETED
        orchestration.content = "Test content"

        # Add the orchestration to the session
        updated_session = self.session_manager.add_orchestration_to_session(
            session.id, orchestration
        )

        # Check the updated session
        self.assertIsNotNone(updated_session)
        self.assertIn("test_orchestration_id", updated_session.orchestrations)

        # Get the orchestration
        retrieved_orchestration = self.session_manager.get_orchestration(
            session.id, "test_orchestration_id"
        )

        # Check the retrieved orchestration
        self.assertIsNotNone(retrieved_orchestration)
        self.assertEqual(retrieved_orchestration.id, orchestration.id)
        self.assertEqual(
            retrieved_orchestration.content, orchestration.content
        )

    def test_session_lifecycle(self):
        """Test the session lifecycle."""
        # Create a session
        session = self.session_manager.create_session()

        # Complete the session
        completed_session = self.session_manager.complete_session(session.id)

        # Check the completed session
        self.assertIsNotNone(completed_session)
        self.assertEqual(completed_session.status, SessionStatus.COMPLETED)

        # Create another session
        session2 = self.session_manager.create_session()

        # Fail the session
        failed_session = self.session_manager.fail_session(session2.id)

        # Check the failed session
        self.assertIsNotNone(failed_session)
        self.assertEqual(failed_session.status, SessionStatus.FAILED)

        # List sessions
        active_sessions = self.session_manager.list_sessions(
            SessionStatus.ACTIVE
        )
        completed_sessions = self.session_manager.list_sessions(
            SessionStatus.COMPLETED
        )
        failed_sessions = self.session_manager.list_sessions(
            SessionStatus.FAILED
        )

        # Check the session lists
        self.assertEqual(len(active_sessions), 0)
        self.assertEqual(len(completed_sessions), 1)
        self.assertEqual(len(failed_sessions), 1)


class TestIntegration(unittest.TestCase):
    """Integration tests for the LLM Orchestrator module."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for session storage
        self.temp_dir = tempfile.mkdtemp()
        self.session_manager = SessionManager(storage_dir=self.temp_dir)

        # Create an orchestrator
        self.orchestrator = OrchestratorFactory.create_default_orchestrator()

    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    async def test_orchestrate_and_store(self):
        """Test orchestrating a prompt and storing the result in a session."""
        # Create a session
        session = self.session_manager.create_session()

        # Set the orchestrator's session ID to match the session
        self.orchestrator.session_id = session.id

        # Define a prompt
        prompt = "Create a dark trap artist with mysterious vibes"

        # Orchestrate the prompt
        result = await self.orchestrator.orchestrate_prompt(prompt)

        # Add the result to the session
        updated_session = self.session_manager.add_orchestration_to_session(
            session.id, result
        )

        # Check the updated session
        self.assertIsNotNone(updated_session)
        self.assertIn(result.id, updated_session.orchestrations)

        # Get the orchestration from the session
        retrieved_result = self.session_manager.get_orchestration(
            session.id, result.id
        )

        # Check the retrieved result
        self.assertIsNotNone(retrieved_result)
        self.assertEqual(retrieved_result.id, result.id)
        self.assertEqual(retrieved_result.content, result.content)
        self.assertEqual(
            retrieved_result.confidence_score, result.confidence_score
        )


def run_async_test(test_func):
    """Run an async test function."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_func())


if __name__ == "__main__":
    # Run the tests
    unittest.main()
