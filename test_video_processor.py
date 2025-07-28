#!/usr/bin/env python3
"""
Test script for VideoProcessor functionality.

This script provides basic tests for the video processing functionality
without requiring actual video files or Ollama installation.
"""

import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from video_processor import VideoProcessor


class TestVideoProcessor(unittest.TestCase):
    """Test cases for VideoProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('video_processor.whisper.load_model')
    @patch('video_processor.ollama.list')
    def test_init(self, mock_ollama_list, mock_whisper_load):
        """Test VideoProcessor initialization."""
        # Mock Whisper model
        mock_whisper_load.return_value = Mock()
        
        # Mock Ollama models list
        mock_ollama_list.return_value = {
            'models': [{'name': 'llama3.1:8b'}]
        }
        
        processor = VideoProcessor(str(self.test_dir))
        
        # Check directories are created
        self.assertTrue((self.test_dir / "transcribed").exists())
        self.assertTrue((self.test_dir / "questions").exists())
        
        # Check initialization calls
        mock_whisper_load.assert_called_once_with("base")
        mock_ollama_list.assert_called_once()
    
    def test_find_video_files(self):
        """Test video file discovery."""
        # Create test files
        (self.test_dir / "video1.mp4").touch()
        (self.test_dir / "video2.avi").touch()
        (self.test_dir / "not_video.txt").touch()
        (self.test_dir / "video3.mov").touch()
        
        with patch('video_processor.whisper.load_model'), \
             patch('video_processor.ollama.list') as mock_ollama:
            mock_ollama.return_value = {'models': [{'name': 'llama3.1:8b'}]}
            
            processor = VideoProcessor(str(self.test_dir))
            video_files = processor.find_video_files()
        
        # Should find 3 video files
        self.assertEqual(len(video_files), 3)
        video_names = [f.name for f in video_files]
        self.assertIn("video1.mp4", video_names)
        self.assertIn("video2.avi", video_names)
        self.assertIn("video3.mov", video_names)
        self.assertNotIn("not_video.txt", video_names)
    
    def test_chunk_text(self):
        """Test text chunking functionality."""
        with patch('video_processor.whisper.load_model'), \
             patch('video_processor.ollama.list') as mock_ollama:
            mock_ollama.return_value = {'models': [{'name': 'llama3.1:8b'}]}
            
            processor = VideoProcessor(str(self.test_dir))
        
        # Test short text (should be one chunk)
        short_text = "This is a short text."
        chunks = processor.chunk_text(short_text)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], short_text)
        
        # Test long text (should be multiple chunks)
        long_text = " ".join(["word"] * 5000)  # Create long text
        chunks = processor.chunk_text(long_text)
        self.assertGreater(len(chunks), 1)
        
        # Verify all chunks combined equal original text
        combined = " ".join(chunks)
        self.assertEqual(combined, long_text)
    
    def test_save_transcript(self):
        """Test transcript saving functionality."""
        with patch('video_processor.whisper.load_model'), \
             patch('video_processor.ollama.list') as mock_ollama:
            mock_ollama.return_value = {'models': [{'name': 'llama3.1:8b'}]}
            
            processor = VideoProcessor(str(self.test_dir))
        
        # Test transcript saving
        video_path = self.test_dir / "test_video.mp4"
        transcript = "This is a test transcript with Russian text: Привет мир!"
        
        saved_path = processor.save_transcript(video_path, transcript)
        
        # Check file was created with correct name
        expected_path = processor.transcribed_dir / "test_video_transcript.txt"
        self.assertEqual(saved_path, expected_path)
        self.assertTrue(saved_path.exists())
        
        # Check content was saved correctly
        with open(saved_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        self.assertEqual(saved_content, transcript)
    
    def test_save_questions(self):
        """Test questions saving functionality."""
        with patch('video_processor.whisper.load_model'), \
             patch('video_processor.ollama.list') as mock_ollama:
            mock_ollama.return_value = {'models': [{'name': 'llama3.1:8b'}]}
            
            processor = VideoProcessor(str(self.test_dir))
        
        # Test data
        video_path = self.test_dir / "test_video.mp4"
        questions = [
            {
                "question": "What is your experience with Python?",
                "speaker": "interviewer",
                "type": "technical"
            },
            {
                "question": "Расскажите о себе",
                "speaker": "interviewer", 
                "type": "general"
            }
        ]
        
        saved_path = processor.save_questions(video_path, questions)
        
        # Check file was created
        expected_path = processor.questions_dir / "test_video_questions.json"
        self.assertEqual(saved_path, expected_path)
        self.assertTrue(saved_path.exists())
        
        # Check content structure
        with open(saved_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['video_name'], 'test_video.mp4')
        self.assertEqual(saved_data['total_questions'], 2)
        self.assertIn('by_speaker', saved_data)
        self.assertIn('by_type', saved_data)
        self.assertEqual(len(saved_data['all_questions']), 2)
    
    def test_parse_questions_manually(self):
        """Test manual question parsing fallback."""
        with patch('video_processor.whisper.load_model'), \
             patch('video_processor.ollama.list') as mock_ollama:
            mock_ollama.return_value = {'models': [{'name': 'llama3.1:8b'}]}
            
            processor = VideoProcessor(str(self.test_dir))
        
        # Test response text with questions
        response_text = """
        Here are some questions found:
        What is your programming experience?
        How do you handle stress?
        Какой у вас опыт работы?
        """
        
        questions = processor._parse_questions_manually(response_text)
        
        # Should find questions with '?' marks
        self.assertGreater(len(questions), 0)
        
        # Check that questions are properly formatted
        for question in questions:
            self.assertIn('question', question)
            self.assertIn('speaker', question)
            self.assertIn('type', question)


class TestIntegration(unittest.TestCase):
    """Integration tests that require mocking external dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('video_processor.VideoFileClip')
    @patch('video_processor.whisper.load_model')
    @patch('video_processor.ollama.list')
    @patch('video_processor.ollama.generate')
    def test_full_video_processing_flow(self, mock_ollama_generate, 
                                       mock_ollama_list, mock_whisper_load,
                                       mock_video_clip):
        """Test the complete video processing workflow."""
        # Setup mocks
        mock_whisper_model = Mock()
        mock_whisper_model.transcribe.return_value = {
            'text': 'What is your experience with Python programming?'
        }
        mock_whisper_load.return_value = mock_whisper_model
        
        mock_ollama_list.return_value = {'models': [{'name': 'llama3.1:8b'}]}
        
        mock_ollama_generate.return_value = {
            'response': '[{"question": "What is your experience with Python programming?", "speaker": "interviewer", "type": "technical"}]'
        }
        
        # Mock video file
        mock_video = Mock()
        mock_audio = Mock()
        mock_video.audio = mock_audio
        mock_video_clip.return_value.__enter__.return_value = mock_video
        
        # Create test video file
        video_file = self.test_dir / "test_interview.mp4"
        video_file.touch()
        
        # Process video
        processor = VideoProcessor(str(self.test_dir))
        transcript_path, questions_path = processor.process_video(video_file)
        
        # Verify files were created
        self.assertTrue(transcript_path.exists())
        self.assertTrue(questions_path.exists())
        
        # Verify content
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()
        self.assertIn('Python programming', transcript_content)
        
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        self.assertEqual(questions_data['total_questions'], 1)


def run_tests():
    """Run all tests."""
    print("Running VideoProcessor tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestVideoProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return True
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)