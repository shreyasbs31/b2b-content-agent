"""
Unit tests for HITLSession dataclass
Tests serialization, deserialization, and state management
"""

import unittest
import json
import tempfile
from datetime import datetime
from pathlib import Path
from dataclasses import asdict

# Import the HITLSession class
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from b2b_content_agent.hitl_flow import HITLSession


# Helper functions to match actual implementation
def session_to_dict(session):
    """Convert session to dict using dataclasses.asdict"""
    return asdict(session)


def session_from_dict(data):
    """Create session from dict"""
    return HITLSession(**data)


class TestHITLSession(unittest.TestCase):
    """Test HITLSession dataclass functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.session_id = "20251104_120000"
        self.input_sources = "Test product information"
        self.started_at = datetime.now().isoformat()
        
    def test_session_creation(self):
        """Test creating a new session"""
        session = HITLSession(
            session_id=self.session_id,
            started_at=self.started_at,
            input_sources=self.input_sources,
            auto_approve=False
        )
        
        self.assertEqual(session.session_id, self.session_id)
        self.assertEqual(session.input_sources, self.input_sources)
        self.assertFalse(session.auto_approve)
        self.assertIsNone(session.completed_at)
        
        # Check all gates start as not approved
        self.assertFalse(session.gate1_approved)
        self.assertFalse(session.gate2_approved)
        self.assertFalse(session.gate3_approved)
        self.assertFalse(session.gate4_approved)
        self.assertFalse(session.gate5_approved)
        
        # Check iteration counters start at 0
        self.assertEqual(session.crew1_iterations, 0)
        self.assertEqual(session.crew2_iterations, 0)
        self.assertEqual(session.crew3_iterations, 0)
        
    def test_session_with_outputs(self):
        """Test session with crew outputs"""
        session = HITLSession(
            session_id=self.session_id,
            started_at=self.started_at,
            input_sources=self.input_sources,
            auto_approve=False,
            product_analysis="# Product Analysis\nTest content",
            persona_library="# Personas\nTest personas",
            content_strategy="# Strategy\nTest strategy"
        )
        
        self.assertIsNotNone(session.product_analysis)
        self.assertIsNotNone(session.persona_library)
        self.assertIsNotNone(session.content_strategy)
        self.assertIn("Product Analysis", session.product_analysis)
        
    def test_session_to_dict(self):
        """Test converting session to dictionary"""
        session = HITLSession(
            session_id=self.session_id,
            started_at=self.started_at,
            input_sources=self.input_sources,
            auto_approve=True,
            product_analysis="Test analysis"
        )
        
        session_dict = session_to_dict(session)
        
        self.assertEqual(session_dict["session_id"], self.session_id)
        self.assertEqual(session_dict["input_sources"], self.input_sources)
        self.assertTrue(session_dict["auto_approve"])
        self.assertEqual(session_dict["product_analysis"], "Test analysis")
        
        # Check datetime is stored as string (ISO format)
        self.assertIsInstance(session_dict["started_at"], str)
        self.assertIn(self.started_at[:10], session_dict["started_at"])  # Check date part
        
    def test_session_from_dict(self):
        """Test creating session from dictionary"""
        session_dict = {
            "session_id": self.session_id,
            "started_at": "2025-11-04T12:00:00.123456",
            "completed_at": None,
            "input_sources": self.input_sources,
            "auto_approve": False,
            "product_analysis": "Test analysis",
            "persona_library": None,
            "content_strategy": None,
            "generated_content": None,
            "final_content": None,
            "gate1_approved": True,
            "gate2_approved": False,
            "gate3_approved": False,
            "gate4_approved": False,
            "gate5_approved": False,
            "crew1_iterations": 2,
            "crew2_iterations": 0,
            "crew3_iterations": 0
        }
        
        session = session_from_dict(session_dict)
        
        self.assertEqual(session.session_id, self.session_id)
        self.assertEqual(session.input_sources, self.input_sources)
        self.assertEqual(session.product_analysis, "Test analysis")
        self.assertTrue(session.gate1_approved)
        self.assertFalse(session.gate2_approved)
        self.assertEqual(session.crew1_iterations, 2)
        
        # Check datetime is stored as string (not parsed to datetime object)
        self.assertIsInstance(session.started_at, str)
        
    def test_session_json_serialization(self):
        """Test full JSON serialization cycle"""
        original_session = HITLSession(
            session_id=self.session_id,
            started_at=self.started_at,
            input_sources=self.input_sources,
            auto_approve=False,
            product_analysis="Analysis content",
            gate1_approved=True,
            crew1_iterations=1
        )
        
        # Convert to dict and JSON
        session_dict = session_to_dict(original_session)
        json_str = json.dumps(session_dict, indent=2)
        
        # Parse back
        parsed_dict = json.loads(json_str)
        restored_session = session_from_dict(parsed_dict)
        
        # Verify all fields match
        self.assertEqual(restored_session.session_id, original_session.session_id)
        self.assertEqual(restored_session.input_sources, original_session.input_sources)
        self.assertEqual(restored_session.product_analysis, original_session.product_analysis)
        self.assertEqual(restored_session.gate1_approved, original_session.gate1_approved)
        self.assertEqual(restored_session.crew1_iterations, original_session.crew1_iterations)
        
    def test_session_save_and_load(self):
        """Test saving and loading session from file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            # Create and save session
            original_session = HITLSession(
                session_id=self.session_id,
                started_at=self.started_at,
                input_sources=self.input_sources,
                auto_approve=False,
                product_analysis="Test analysis",
                persona_library="Test personas",
                gate1_approved=True,
                gate2_approved=True,
                crew1_iterations=2
            )
            
            # Save to file using session's save method
            session_file = original_session.save(output_dir)
            
            # Load from file
            with open(session_file, 'r') as f:
                loaded_dict = json.load(f)
            
            restored_session = session_from_dict(loaded_dict)
            
            # Verify
            self.assertEqual(restored_session.session_id, original_session.session_id)
            self.assertEqual(restored_session.product_analysis, original_session.product_analysis)
            self.assertEqual(restored_session.persona_library, original_session.persona_library)
            self.assertTrue(restored_session.gate1_approved)
            self.assertTrue(restored_session.gate2_approved)
            self.assertEqual(restored_session.crew1_iterations, 2)
            
    def test_session_with_dict_outputs(self):
        """Test session with dictionary outputs (CREW 2 and 3)"""
        # Note: In actual implementation, these are stored as strings, not dicts
        generated_content = "Case studies, white papers, etc."
        final_content = "QA, brand, SEO reports"
        
        session = HITLSession(
            session_id=self.session_id,
            started_at=self.started_at,
            input_sources=self.input_sources,
            auto_approve=False,
            generated_content=generated_content,
            final_content=final_content
        )
        
        # Test asdict preserves content
        session_dict = session_to_dict(session)
        self.assertEqual(session_dict["generated_content"], generated_content)
        self.assertEqual(session_dict["final_content"], final_content)
        
        # Test from_dict restores content
        restored_session = session_from_dict(session_dict)
        self.assertEqual(restored_session.generated_content, generated_content)
        
    def test_gate_progression(self):
        """Test logical gate progression"""
        session = HITLSession(
            session_id=self.session_id,
            started_at=self.started_at,
            input_sources=self.input_sources,
            auto_approve=False
        )
        
        # Simulate gate progression
        session.gate1_approved = True
        self.assertTrue(session.gate1_approved)
        self.assertFalse(session.gate2_approved)
        
        session.gate2_approved = True
        session.gate3_approved = True
        self.assertTrue(session.gate3_approved)
        self.assertFalse(session.gate4_approved)
        
        # All gates approved
        session.gate4_approved = True
        session.gate5_approved = True
        self.assertTrue(all([
            session.gate1_approved,
            session.gate2_approved,
            session.gate3_approved,
            session.gate4_approved,
            session.gate5_approved
        ]))
        
    def test_iteration_tracking(self):
        """Test iteration counter behavior"""
        session = HITLSession(
            session_id=self.session_id,
            started_at=self.started_at,
            input_sources=self.input_sources,
            auto_approve=False
        )
        
        # Simulate feedback loops
        self.assertEqual(session.crew1_iterations, 0)
        
        session.crew1_iterations += 1
        self.assertEqual(session.crew1_iterations, 1)
        
        session.crew1_iterations += 1
        session.crew1_iterations += 1
        self.assertEqual(session.crew1_iterations, 3)
        
        # Other crews unaffected
        self.assertEqual(session.crew2_iterations, 0)
        self.assertEqual(session.crew3_iterations, 0)
        
    def test_completion_timestamp(self):
        """Test setting completion timestamp"""
        session = HITLSession(
            session_id=self.session_id,
            started_at=self.started_at,
            input_sources=self.input_sources,
            auto_approve=False
        )
        
        self.assertIsNone(session.completed_at)
        
        # Mark as completed
        completed_time = datetime.now().isoformat()
        session.completed_at = completed_time
        self.assertIsNotNone(session.completed_at)
        self.assertIsInstance(session.completed_at, str)
        
        # Verify serialization handles it
        session_dict = session_to_dict(session)
        self.assertIsInstance(session_dict["completed_at"], str)
        
        restored_session = session_from_dict(session_dict)
        self.assertIsInstance(restored_session.completed_at, str)


class TestHITLSessionEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_empty_session_id(self):
        """Test session with empty ID still works"""
        session = HITLSession(
            session_id="",
            started_at=datetime.now().isoformat(),
            input_sources="Test",
            auto_approve=False
        )
        self.assertEqual(session.session_id, "")
        
    def test_very_long_content(self):
        """Test session with very long content"""
        long_content = "x" * 100000  # 100KB of content
        
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test",
            auto_approve=False,
            product_analysis=long_content
        )
        
        # Should serialize and deserialize without issues
        session_dict = session_to_dict(session)
        self.assertEqual(len(session_dict["product_analysis"]), 100000)
        
        restored = session_from_dict(session_dict)
        self.assertEqual(len(restored.product_analysis), 100000)
        
    def test_special_characters_in_content(self):
        """Test content with special characters"""
        special_content = "Content with 'quotes', \"double quotes\", \n newlines, \t tabs, and émojis 🚀"
        
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources=special_content,
            auto_approve=False,
            product_analysis=special_content
        )
        
        # Should handle JSON encoding
        session_dict = session_to_dict(session)
        json_str = json.dumps(session_dict)
        
        # Should parse back correctly
        parsed = json.loads(json_str)
        restored = session_from_dict(parsed)
        self.assertEqual(restored.input_sources, special_content)
        self.assertEqual(restored.product_analysis, special_content)
        
    def test_none_values(self):
        """Test session with many None values"""
        session = HITLSession(
            session_id="test",
            started_at=datetime.now().isoformat(),
            input_sources="Test",
            auto_approve=False,
            product_analysis=None,
            persona_library=None,
            content_strategy=None,
            generated_content=None,
            final_content=None,
            completed_at=None
        )
        
        session_dict = session_to_dict(session)
        self.assertIsNone(session_dict["product_analysis"])
        self.assertIsNone(session_dict["completed_at"])
        
        restored = session_from_dict(session_dict)
        self.assertIsNone(restored.product_analysis)
        self.assertIsNone(restored.completed_at)


if __name__ == "__main__":
    unittest.main()
