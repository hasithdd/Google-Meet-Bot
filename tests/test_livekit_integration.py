"""Tests for LiveKit Agent Integration.

These tests verify that the LiveKit integration module works correctly.
Note: These are unit tests that don't require actual LiveKit credentials.
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestLiveKitAgentImports(unittest.TestCase):
    """Test that LiveKit agent module can be imported."""
    
    def test_module_imports(self):
        """Test that the livekit_agent module can be imported."""
        try:
            from google_meet_bot import livekit_agent
            self.assertIsNotNone(livekit_agent)
        except ImportError:
            # If it fails due to missing dependencies, that's expected
            self.skipTest("LiveKit dependencies not available")
    
    def test_is_livekit_available_function(self):
        """Test the is_livekit_available function."""
        try:
            from google_meet_bot.livekit_agent import is_livekit_available
            result = is_livekit_available()
            self.assertIsInstance(result, bool)
        except ImportError:
            self.skipTest("LiveKit dependencies not available")


class TestLiveKitAgentManager(unittest.TestCase):
    """Test LiveKitAgentManager class."""
    
    @patch.dict(os.environ, {
        'LIVEKIT_URL': 'wss://test.livekit.io',
        'LIVEKIT_API_KEY': 'test_key',
        'LIVEKIT_API_SECRET': 'test_secret',
        'OPENAI_API_KEY': 'test_openai_key'
    })
    def test_manager_init_with_credentials(self):
        """Test LiveKitAgentManager initialization with credentials."""
        try:
            from google_meet_bot.livekit_agent import LiveKitAgentManager
            # This should work if credentials are set
            # But will fail if LiveKit is not installed, which is expected
            try:
                manager = LiveKitAgentManager()
                self.assertIsNotNone(manager.livekit_url)
                self.assertEqual(manager.livekit_url, 'wss://test.livekit.io')
            except ImportError as e:
                if 'LiveKit packages are not installed' in str(e):
                    self.skipTest("LiveKit packages not installed")
                raise
        except ImportError:
            self.skipTest("LiveKit module not available")
    
    def test_manager_init_without_credentials(self):
        """Test LiveKitAgentManager initialization without credentials."""
        try:
            from google_meet_bot.livekit_agent import LiveKitAgentManager
            # Clear environment variables
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises((ValueError, ImportError)):
                    LiveKitAgentManager()
        except ImportError:
            self.skipTest("LiveKit module not available")


class TestJoinGoogleMeetWithLiveKit(unittest.TestCase):
    """Test JoinGoogleMeet with LiveKit integration."""
    
    @patch.dict(os.environ, {
        'EMAIL_ID': 'test@example.com',
        'EMAIL_PASSWORD': 'password'
    })
    @patch('google_meet_bot.join_google_meet.webdriver.Chrome')
    def test_join_google_meet_with_livekit_disabled(self, mock_chrome):
        """Test JoinGoogleMeet initialization with LiveKit disabled."""
        try:
            from google_meet_bot import JoinGoogleMeet
            
            # Create instance with LiveKit disabled
            bot = JoinGoogleMeet(enable_livekit=False)
            self.assertFalse(bot.enable_livekit)
            self.assertIsNone(bot.livekit_manager)
            self.assertIsNone(bot.livekit_bridge)
        except Exception as e:
            # If it fails due to selenium/browser issues, that's expected in test env
            if 'PortAudio' in str(e) or 'Chrome' in str(e):
                self.skipTest(f"Expected failure in test environment: {e}")
            raise
    
    @patch.dict(os.environ, {
        'EMAIL_ID': 'test@example.com',
        'EMAIL_PASSWORD': 'password',
        'LIVEKIT_URL': 'wss://test.livekit.io',
        'LIVEKIT_API_KEY': 'test_key',
        'LIVEKIT_API_SECRET': 'test_secret',
        'OPENAI_API_KEY': 'test_openai_key'
    })
    @patch('google_meet_bot.join_google_meet.webdriver.Chrome')
    def test_join_google_meet_with_livekit_enabled(self, mock_chrome):
        """Test JoinGoogleMeet initialization with LiveKit enabled."""
        try:
            from google_meet_bot import JoinGoogleMeet
            
            # Create instance with LiveKit enabled
            bot = JoinGoogleMeet(enable_livekit=True)
            # If LiveKit packages are installed, these should be set
            # If not, enable_livekit should be False
            if bot.enable_livekit:
                self.assertIsNotNone(bot.livekit_manager)
                self.assertIsNotNone(bot.livekit_bridge)
            else:
                # LiveKit not available, that's ok
                pass
        except Exception as e:
            # If it fails due to selenium/browser issues, that's expected in test env
            if 'PortAudio' in str(e) or 'Chrome' in str(e):
                self.skipTest(f"Expected failure in test environment: {e}")
            raise


class TestLiveKitWorker(unittest.TestCase):
    """Test LiveKit worker module."""
    
    def test_worker_module_syntax(self):
        """Test that the worker module has valid syntax."""
        import py_compile
        import tempfile
        
        worker_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'src',
            'google_meet_bot',
            'livekit_worker.py'
        )
        
        # Try to compile the module
        try:
            with tempfile.NamedTemporaryFile(suffix='.pyc', delete=False) as f:
                py_compile.compile(worker_path, f.name, doraise=True)
                os.unlink(f.name)
            # If we got here, syntax is valid
            self.assertTrue(True)
        except py_compile.PyCompileError as e:
            self.fail(f"Worker module has syntax errors: {e}")


if __name__ == '__main__':
    unittest.main()
