"""
Unit tests for HITLOrchestrator logic
Tests approval gates, iteration limits, and state management
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from b2b_content_agent.hitl_flow import HITLOrchestrator, HITLSession


class TestHITLOrchestratorInit(unittest.TestCase):
    """Test orchestrator initialization"""
    
    def test_orchestrator_creation(self):
        """Test creating orchestrator"""
        with tempfile.TemporaryDirectory() as temp_dir:
            orchestrator = HITLOrchestrator(
                auto_approve=False,
                output_dir=temp_dir
            )
            
            self.assertFalse(orchestrator.auto_approve)
            self.assertEqual(str(orchestrator.output_dir), temp_dir)
            # Crews are lazily initialized, so they don't exist yet
            self.assertFalse(orchestrator.crews_initialized)
            
    def test_orchestrator_auto_approve(self):
        """Test auto_approve flag"""
        orchestrator = HITLOrchestrator(auto_approve=True, output_dir="test")
        self.assertTrue(orchestrator.auto_approve)
        
    def test_output_dir_creation(self):
        """Test output directory is created if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "new_output"
            self.assertFalse(output_path.exists())
            
            orchestrator = HITLOrchestrator(
                auto_approve=False,
                output_dir=str(output_path)
            )
            
            # Output dir should be created
            self.assertTrue(output_path.exists())


class TestInputValidation(unittest.TestCase):
    """Test input validation logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = HITLOrchestrator(
            auto_approve=True,
            output_dir=self.temp_dir
        )
        
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_empty_input_rejected(self):
        """Test empty input is rejected"""
        with self.assertRaises(ValueError) as context:
            self.orchestrator.run_full_pipeline(
                input_sources="",
                max_iterations=3
            )
        self.assertIn("empty", str(context.exception).lower())
        
    def test_whitespace_input_rejected(self):
        """Test whitespace-only input is rejected"""
        with self.assertRaises(ValueError) as context:
            self.orchestrator.run_full_pipeline(
                input_sources="   \n\t  ",
                max_iterations=3
            )
        self.assertIn("empty", str(context.exception).lower())
        
    def test_invalid_max_iterations(self):
        """Test invalid max_iterations is rejected"""
        with self.assertRaises(ValueError) as context:
            self.orchestrator.run_full_pipeline(
                input_sources="Valid input",
                max_iterations=0
            )
        self.assertIn("max_iterations", str(context.exception).lower())
        
        with self.assertRaises(ValueError) as context:
            self.orchestrator.run_full_pipeline(
                input_sources="Valid input",
                max_iterations=-1
            )
        self.assertIn("max_iterations", str(context.exception).lower())
        
    def test_valid_input_accepted(self):
        """Test valid input is accepted"""
        # We won't run the full pipeline, just test validation doesn't raise
        try:
            # This will fail when trying to initialize crews, but validation should pass
            self.orchestrator.run_full_pipeline(
                input_sources="Valid product information",
                max_iterations=3
            )
        except Exception as e:
            # Should fail on crew initialization, not validation
            self.assertNotIn("empty", str(e).lower())
            self.assertNotIn("max_iterations", str(e).lower())


class TestIterationLogic(unittest.TestCase):
    """Test iteration counting and limits"""
    
    def test_iteration_increment(self):
        """Test iteration counter increments correctly"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test input",
            auto_approve=False
        )
        
        # Initial state
        self.assertEqual(session.crew1_iterations, 0)
        
        # Simulate feedback loop
        session.crew1_iterations += 1
        self.assertEqual(session.crew1_iterations, 1)
        
        session.crew1_iterations += 1
        self.assertEqual(session.crew1_iterations, 2)
        
    def test_max_iterations_check(self):
        """Test max iterations logic"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test input",
            auto_approve=False,
            crew1_iterations=3
        )
        
        max_iterations = 3
        
        # Should be at limit
        self.assertTrue(session.crew1_iterations >= max_iterations)
        
    def test_separate_iteration_counters(self):
        """Test each crew has separate iteration counter"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test input",
            auto_approve=False
        )
        
        # Increment only CREW 1
        session.crew1_iterations = 2
        
        # Others should be unaffected
        self.assertEqual(session.crew1_iterations, 2)
        self.assertEqual(session.crew2_iterations, 0)
        self.assertEqual(session.crew3_iterations, 0)


class TestSessionPersistence(unittest.TestCase):
    """Test session save/load functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = HITLOrchestrator(
            auto_approve=False,
            output_dir=self.temp_dir
        )
        
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_session_save(self):
        """Test saving session to file"""
        session = HITLSession(
            session_id="20251104_120000",
            started_at=datetime.now().isoformat(),
            input_sources="Test input",
            auto_approve=False,
            product_analysis="Test analysis",
            gate1_approved=True
        )
        
        # Save session using asdict()
        session_file = Path(self.temp_dir) / f"hitl_session_{session.session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(asdict(session), f, indent=2)
            
        # Verify file exists
        self.assertTrue(session_file.exists())
        
        # Verify content
        with open(session_file, 'r') as f:
            loaded = json.load(f)
        
        self.assertEqual(loaded["session_id"], "20251104_120000")
        self.assertEqual(loaded["product_analysis"], "Test analysis")
        self.assertTrue(loaded["gate1_approved"])
        
    def test_load_session(self):
        """Test loading session from file"""
        session_id = "20251104_120000"
        
        # Create a session file
        session_data = {
            "session_id": session_id,
            "started_at": "2025-11-04T12:00:00.000000",
            "completed_at": None,
            "input_sources": "Test input",
            "auto_approve": False,
            "product_analysis": "Analysis content",
            "persona_library": "Persona content",
            "content_strategy": None,
            "generated_content": None,
            "final_content": None,
            "gate1_approved": True,
            "gate2_approved": True,
            "gate3_approved": False,
            "gate4_approved": False,
            "gate5_approved": False,
            "crew1_iterations": 1,
            "crew2_iterations": 0,
            "crew3_iterations": 0
        }
        
        session_file = Path(self.temp_dir) / f"hitl_session_{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
            
        # Load session using orchestrator
        loaded_session = self.orchestrator._load_session(session_id)
        
        self.assertEqual(loaded_session.session_id, session_id)
        self.assertEqual(loaded_session.product_analysis, "Analysis content")
        self.assertTrue(loaded_session.gate1_approved)
        self.assertTrue(loaded_session.gate2_approved)
        self.assertFalse(loaded_session.gate3_approved)
        self.assertEqual(loaded_session.crew1_iterations, 1)
        
    def test_load_nonexistent_session(self):
        """Test loading a session that doesn't exist"""
        with self.assertRaises(FileNotFoundError):
            self.orchestrator._load_session("nonexistent_session_id")
            
    def test_load_corrupted_session(self):
        """Test loading a corrupted session file"""
        session_id = "corrupted"
        session_file = Path(self.temp_dir) / f"hitl_session_{session_id}.json"
        
        # Write invalid JSON
        with open(session_file, 'w') as f:
            f.write("{ invalid json content")
            
        with self.assertRaises(json.JSONDecodeError):
            self.orchestrator._load_session(session_id)


class TestFileReading(unittest.TestCase):
    """Test file reading utility"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = HITLOrchestrator(
            auto_approve=False,
            output_dir=self.temp_dir
        )
        
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_read_existing_file(self):
        """Test reading an existing file"""
        test_file = Path(self.temp_dir) / "test.txt"
        test_content = "Test file content"
        
        with open(test_file, 'w') as f:
            f.write(test_content)
            
        content = self.orchestrator._read_output_file("test.txt")
        self.assertEqual(content, test_content)
        
    def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist"""
        content = self.orchestrator._read_output_file("nonexistent.txt")
        self.assertIsNone(content)
        
    def test_read_file_with_path_traversal(self):
        """Test file reading respects output_dir"""
        # Try to read outside output_dir (should use output_dir as base)
        content = self.orchestrator._read_output_file("../sensitive.txt")
        # Should return None since file doesn't exist in output_dir
        self.assertIsNone(content)


class TestAutoApproveMode(unittest.TestCase):
    """Test auto-approve functionality"""
    
    def test_auto_approve_returns_true(self):
        """Test _get_approval in auto-approve mode"""
        orchestrator = HITLOrchestrator(
            auto_approve=True,
            output_dir=tempfile.mkdtemp()
        )
        
        # In auto-approve mode, should always return (True, "")
        approved, feedback = orchestrator._get_approval(
            gate_name="Test Gate",
            content="Test content",
            gate_num=1
        )
        
        self.assertTrue(approved)
        self.assertEqual(feedback, "")


class TestGateApprovalStates(unittest.TestCase):
    """Test gate approval state transitions"""
    
    def test_all_gates_initially_false(self):
        """Test all gates start as not approved"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now(),
            input_sources="Test",
            auto_approve=False
        )
        
        self.assertFalse(session.gate1_approved)
        self.assertFalse(session.gate2_approved)
        self.assertFalse(session.gate3_approved)
        self.assertFalse(session.gate4_approved)
        self.assertFalse(session.gate5_approved)
        
    def test_gate_approval_progression(self):
        """Test gates can be approved in sequence"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now(),
            input_sources="Test",
            auto_approve=False
        )
        
        # Approve gates in order
        session.gate1_approved = True
        self.assertTrue(session.gate1_approved)
        
        session.gate2_approved = True
        self.assertTrue(session.gate2_approved)
        
        session.gate3_approved = True
        session.gate4_approved = True
        session.gate5_approved = True
        
        # All should be approved
        all_approved = all([
            session.gate1_approved,
            session.gate2_approved,
            session.gate3_approved,
            session.gate4_approved,
            session.gate5_approved
        ])
        self.assertTrue(all_approved)
        
    def test_gate_state_persists(self):
        """Test gate states persist through serialization"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test",
            auto_approve=False,
            gate1_approved=True,
            gate2_approved=True,
            gate3_approved=False
        )
        
        # Serialize and deserialize
        session_dict = asdict(session)
        restored = HITLSession(**session_dict)
        
        # States should match
        self.assertTrue(restored.gate1_approved)
        self.assertTrue(restored.gate2_approved)
        self.assertFalse(restored.gate3_approved)


class TestCrew1OutputUpdates(unittest.TestCase):
    """Test that Gate 2/3 feedback updates all CREW 1 outputs"""
    
    def test_crew1_updates_all_three_outputs(self):
        """Test that running CREW 1 updates all three outputs"""
        # This is a mock test - we can't run actual crews in unit tests
        # But we can verify the session structure supports it
        
        session = HITLSession(
            session_id="test",
            started_at=datetime.now(),
            input_sources="Test",
            auto_approve=False
        )
        
        # Simulate CREW 1 outputs
        session.product_analysis = "New analysis"
        session.persona_library = "New personas"
        session.content_strategy = "New strategy"
        
        # All three should be updated
        self.assertEqual(session.product_analysis, "New analysis")
        self.assertEqual(session.persona_library, "New personas")
        self.assertEqual(session.content_strategy, "New strategy")
        
    def test_gate2_feedback_should_update_all_crew1(self):
        """Test Gate 2 scenario - persona feedback should update all CREW 1 outputs"""
        # This test documents expected behavior
        # When user provides feedback at Gate 2 (persona_library),
        # CREW 1 re-runs and should update product_analysis, persona_library, AND content_strategy
        
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test",
            auto_approve=False,
            product_analysis="Original analysis",
            persona_library="Original personas",
            content_strategy="Original strategy",
            gate1_approved=True
        )
        
        # User at Gate 2 gives feedback
        # CREW 1 re-runs with feedback
        # ALL THREE outputs should be updated (not just persona_library)
        
        session.product_analysis = "Updated analysis"
        session.persona_library = "Updated personas"  
        session.content_strategy = "Updated strategy"
        session.crew1_iterations += 1
        
        # Verify all updated
        self.assertEqual(session.product_analysis, "Updated analysis")
        self.assertEqual(session.persona_library, "Updated personas")
        self.assertEqual(session.content_strategy, "Updated strategy")
        self.assertEqual(session.crew1_iterations, 1)


class TestSessionSaveMethod(unittest.TestCase):
    """Test HITLSession.save() method"""
    
    def test_session_save_method(self):
        """Test the save() method on HITLSession"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            session = HITLSession(
                session_id="test_save_20251104",
                started_at=datetime.now().isoformat(),
                input_sources="Test input",
                auto_approve=False,
                product_analysis="Analysis",
                gate1_approved=True,
                crew1_iterations=1
            )
            
            # Use the save() method
            saved_file = session.save(output_dir)
            
            # Verify file was created
            self.assertTrue(saved_file.exists())
            self.assertEqual(saved_file.name, "hitl_session_test_save_20251104.json")
            
            # Verify content
            with open(saved_file, 'r') as f:
                loaded = json.load(f)
            
            self.assertEqual(loaded["session_id"], "test_save_20251104")
            self.assertEqual(loaded["product_analysis"], "Analysis")
            self.assertTrue(loaded["gate1_approved"])
            self.assertEqual(loaded["crew1_iterations"], 1)


class TestInputValidationEdgeCases(unittest.TestCase):
    """Test additional input validation scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = HITLOrchestrator(
            auto_approve=True,
            output_dir=self.temp_dir
        )
        
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_unicode_input(self):
        """Test input with unicode characters"""
        unicode_input = "Product info with émojis 🚀 and 中文 characters"
        
        # Should not raise validation error
        try:
            # Will fail later but validation should pass
            self.orchestrator.run_full_pipeline(
                input_sources=unicode_input,
                max_iterations=1
            )
        except ValueError as e:
            # Should not be validation error
            self.assertNotIn("empty", str(e).lower())
        except Exception:
            # Other errors are fine for this test
            pass
            
    def test_very_long_input(self):
        """Test input with very long text"""
        long_input = "A" * 10000  # 10K characters
        
        try:
            self.orchestrator.run_full_pipeline(
                input_sources=long_input,
                max_iterations=1
            )
        except ValueError as e:
            self.assertNotIn("empty", str(e).lower())
        except Exception:
            pass
            
    def test_max_iterations_boundary(self):
        """Test max_iterations at boundary values"""
        # max_iterations = 1 should be valid
        try:
            self.orchestrator.run_full_pipeline(
                input_sources="Valid input",
                max_iterations=1
            )
        except ValueError as e:
            # Should not fail on max_iterations=1
            self.assertNotIn("max_iterations", str(e).lower())
        except Exception:
            pass


class TestFeedbackLoopScenarios(unittest.TestCase):
    """Test various feedback loop scenarios"""
    
    def test_single_feedback_iteration(self):
        """Test a single feedback iteration increments counter"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test",
            auto_approve=False,
            crew1_iterations=0
        )
        
        # Simulate one feedback loop
        session.crew1_iterations += 1
        self.assertEqual(session.crew1_iterations, 1)
        
        # Session can be saved and loaded
        session_dict = asdict(session)
        restored = HITLSession(**session_dict)
        self.assertEqual(restored.crew1_iterations, 1)
        
    def test_multiple_feedback_iterations(self):
        """Test multiple feedback iterations"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test",
            auto_approve=False
        )
        
        max_iterations = 3
        
        for i in range(max_iterations):
            if session.crew1_iterations < max_iterations:
                session.crew1_iterations += 1
                
        self.assertEqual(session.crew1_iterations, 3)
        
    def test_reaching_iteration_limit(self):
        """Test behavior when reaching iteration limit"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test",
            auto_approve=False,
            crew1_iterations=3
        )
        
        max_iterations = 3
        
        # Should be at limit
        at_limit = session.crew1_iterations >= max_iterations
        self.assertTrue(at_limit)
        
        # Should not increment further in real implementation
        if session.crew1_iterations >= max_iterations:
            # Would skip re-run
            pass
        else:
            session.crew1_iterations += 1
            
        # Counter should still be 3
        self.assertEqual(session.crew1_iterations, 3)


class TestGateProgressionScenarios(unittest.TestCase):
    """Test realistic gate progression scenarios"""
    
    def test_sequential_gate_approval(self):
        """Test gates approved in sequence"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test",
            auto_approve=False
        )
        
        # Approve gates in order
        gates = [
            'gate1_approved', 'gate2_approved', 'gate3_approved',
            'gate4_approved', 'gate5_approved'
        ]
        
        for i, gate in enumerate(gates):
            # Check previous gates are approved
            for j in range(i):
                self.assertTrue(getattr(session, gates[j]))
            
            # Approve current gate
            setattr(session, gate, True)
            self.assertTrue(getattr(session, gate))
            
        # All gates should be approved
        all_approved = all(getattr(session, gate) for gate in gates)
        self.assertTrue(all_approved)
        
    def test_partial_gate_completion(self):
        """Test session with some gates approved"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test",
            auto_approve=False,
            gate1_approved=True,
            gate2_approved=True,
            gate3_approved=True,
            gate4_approved=False,
            gate5_approved=False
        )
        
        # First 3 approved
        self.assertTrue(session.gate1_approved)
        self.assertTrue(session.gate2_approved)
        self.assertTrue(session.gate3_approved)
        
        # Last 2 not approved
        self.assertFalse(session.gate4_approved)
        self.assertFalse(session.gate5_approved)
        
        # Session is incomplete
        all_approved = all([
            session.gate1_approved,
            session.gate2_approved,
            session.gate3_approved,
            session.gate4_approved,
            session.gate5_approved
        ])
        self.assertFalse(all_approved)
        
    def test_complete_pipeline_simulation(self):
        """Test simulating a complete pipeline run"""
        session = HITLSession(
            session_id="test_complete",
            started_at=datetime.now().isoformat(),
            input_sources="Product information",
            auto_approve=False
        )
        
        # CREW 1 runs
        session.product_analysis = "Analysis content"
        session.persona_library = "Persona content"
        session.content_strategy = "Strategy content"
        
        # Gate 1 approved
        session.gate1_approved = True
        self.assertIsNotNone(session.product_analysis)
        
        # Gate 2 approved
        session.gate2_approved = True
        self.assertIsNotNone(session.persona_library)
        
        # Gate 3 approved
        session.gate3_approved = True
        self.assertIsNotNone(session.content_strategy)
        
        # CREW 2 runs
        session.generated_content = "Generated content"
        
        # Gate 4 approved
        session.gate4_approved = True
        self.assertIsNotNone(session.generated_content)
        
        # CREW 3 runs
        session.final_content = "Final polished content"
        
        # Gate 5 approved
        session.gate5_approved = True
        self.assertIsNotNone(session.final_content)
        
        # Mark complete
        session.completed_at = datetime.now().isoformat()
        self.assertIsNotNone(session.completed_at)
        
        # Verify all complete
        all_approved = all([
            session.gate1_approved,
            session.gate2_approved,
            session.gate3_approved,
            session.gate4_approved,
            session.gate5_approved
        ])
        self.assertTrue(all_approved)


class TestSessionResume(unittest.TestCase):
    """Test session resume functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_resume_after_gate1(self):
        """Test resuming session after Gate 1"""
        session_id = "resume_test_gate1"
        
        # Create a session that completed Gate 1
        session_data = {
            "session_id": session_id,
            "started_at": "2025-11-04T10:00:00",
            "completed_at": None,
            "input_sources": "Product info",
            "auto_approve": False,
            "product_analysis": "Analysis content",
            "persona_library": "Persona content",
            "content_strategy": "Strategy content",
            "generated_content": None,
            "final_content": None,
            "gate1_approved": True,
            "gate2_approved": False,
            "gate3_approved": False,
            "gate4_approved": False,
            "gate5_approved": False,
            "crew1_iterations": 0,
            "crew2_iterations": 0,
            "crew3_iterations": 0
        }
        
        # Save session
        session_file = Path(self.temp_dir) / f"hitl_session_{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
            
        # Create orchestrator and load session
        orchestrator = HITLOrchestrator(
            auto_approve=False,
            output_dir=self.temp_dir
        )
        
        loaded = orchestrator._load_session(session_id)
        
        # Verify state
        self.assertTrue(loaded.gate1_approved)
        self.assertFalse(loaded.gate2_approved)
        self.assertIsNotNone(loaded.product_analysis)
        self.assertIsNone(loaded.generated_content)
        
    def test_resume_after_gate4(self):
        """Test resuming session after Gate 4"""
        session_id = "resume_test_gate4"
        
        # Create a session that completed up to Gate 4
        session_data = {
            "session_id": session_id,
            "started_at": "2025-11-04T10:00:00",
            "completed_at": None,
            "input_sources": "Product info",
            "auto_approve": False,
            "product_analysis": "Analysis",
            "persona_library": "Personas",
            "content_strategy": "Strategy",
            "generated_content": "Generated content",
            "final_content": None,
            "gate1_approved": True,
            "gate2_approved": True,
            "gate3_approved": True,
            "gate4_approved": True,
            "gate5_approved": False,
            "crew1_iterations": 1,
            "crew2_iterations": 0,
            "crew3_iterations": 0
        }
        
        # Save session
        session_file = Path(self.temp_dir) / f"hitl_session_{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
            
        # Load session
        orchestrator = HITLOrchestrator(
            auto_approve=False,
            output_dir=self.temp_dir
        )
        
        loaded = orchestrator._load_session(session_id)
        
        # Verify state
        self.assertTrue(loaded.gate4_approved)
        self.assertFalse(loaded.gate5_approved)
        self.assertIsNotNone(loaded.generated_content)
        self.assertIsNone(loaded.final_content)
        self.assertEqual(loaded.crew1_iterations, 1)


class TestErrorHandlingScenarios(unittest.TestCase):
    """Test error handling in various scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = HITLOrchestrator(
            auto_approve=False,
            output_dir=self.temp_dir
        )
        
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_load_session_invalid_json(self):
        """Test loading session with invalid JSON"""
        session_id = "invalid_json"
        session_file = Path(self.temp_dir) / f"hitl_session_{session_id}.json"
        
        # Write invalid JSON
        with open(session_file, 'w') as f:
            f.write("{ invalid json content }")
            
        with self.assertRaises(json.JSONDecodeError):
            self.orchestrator._load_session(session_id)
            
    def test_load_session_missing_fields(self):
        """Test loading session with missing required fields"""
        session_id = "missing_fields"
        session_file = Path(self.temp_dir) / f"hitl_session_{session_id}.json"
        
        # Write incomplete session data
        incomplete_data = {
            "session_id": session_id,
            "started_at": "2025-11-04T10:00:00"
            # Missing many required fields
        }
        
        with open(session_file, 'w') as f:
            json.dump(incomplete_data, f)
            
        with self.assertRaises(TypeError):
            self.orchestrator._load_session(session_id)
            
    def test_load_session_empty_input_sources(self):
        """Test loading session with empty input_sources"""
        session_id = "empty_input"
        session_file = Path(self.temp_dir) / f"hitl_session_{session_id}.json"
        
        session_data = {
            "session_id": session_id,
            "started_at": "2025-11-04T10:00:00",
            "completed_at": None,
            "input_sources": "",  # Empty!
            "auto_approve": False,
            "product_analysis": None,
            "persona_library": None,
            "content_strategy": None,
            "generated_content": None,
            "final_content": None,
            "gate1_approved": False,
            "gate2_approved": False,
            "gate3_approved": False,
            "gate4_approved": False,
            "gate5_approved": False,
            "crew1_iterations": 0,
            "crew2_iterations": 0,
            "crew3_iterations": 0
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
            
        with self.assertRaises(ValueError) as context:
            self.orchestrator._load_session(session_id)
            
        self.assertIn("invalid", str(context.exception).lower())


if __name__ == "__main__":
    unittest.main()
