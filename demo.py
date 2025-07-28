#!/usr/bin/env python3
"""
Example usage and demo script for VideoProcessor.

This script demonstrates how to use the VideoProcessor in different scenarios
and provides example code for customization.
"""

import sys
from pathlib import Path
import logging

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from video_processor import VideoProcessor


def demo_basic_usage():
    """Demonstrate basic usage of VideoProcessor."""
    print("=== Basic Usage Demo ===")
    
    try:
        # Initialize processor for current directory
        processor = VideoProcessor(".")
        
        # Find video files
        video_files = processor.find_video_files()
        print(f"Found {len(video_files)} video files:")
        for video in video_files:
            print(f"  - {video.name}")
        
        if video_files:
            print("\nTo process all videos, run:")
            print("python video_processor.py")
        else:
            print("\nNo video files found in current directory.")
            print("Add some video files and try again!")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Ollama is installed and running.")


def demo_custom_settings():
    """Demonstrate custom settings and configuration."""
    print("\n=== Custom Settings Demo ===")
    
    # Example of customizing the processor
    print("You can customize the VideoProcessor by:")
    print("1. Changing the Ollama model:")
    print("   processor.OLLAMA_MODEL = 'mistral:7b'")
    print()
    print("2. Adjusting chunk size:")
    print("   processor.MAX_CHUNK_TOKENS = 2000")
    print()
    print("3. Using different output directories:")
    print("   processor = VideoProcessor('/path/to/videos')")


def demo_file_structure():
    """Show expected file structure and outputs."""
    print("\n=== File Structure Demo ===")
    
    print("Input structure:")
    print("📁 your_project_folder/")
    print("  📄 video_processor.py")
    print("  📹 interview1.mp4")
    print("  📹 interview2.avi")
    print("  📹 meeting.mov")
    print()
    print("Output structure after processing:")
    print("📁 your_project_folder/")
    print("  📄 video_processor.py")
    print("  📹 interview1.mp4")
    print("  📹 interview2.avi") 
    print("  📹 meeting.mov")
    print("  📁 transcribed/")
    print("    📄 interview1_transcript.txt")
    print("    📄 interview2_transcript.txt")
    print("    📄 meeting_transcript.txt")
    print("  📁 questions/")
    print("    📄 interview1_questions.json")
    print("    📄 interview2_questions.json")
    print("    📄 meeting_questions.json")
    print("  📄 video_processor.log")


def demo_question_format():
    """Show example question output format."""
    print("\n=== Question Format Demo ===")
    
    example_question = {
        "video_name": "technical_interview.mp4",
        "total_questions": 3,
        "by_speaker": {
            "interviewer": [
                {
                    "question": "Расскажите о вашем опыте с Python",
                    "speaker": "interviewer",
                    "type": "technical"
                },
                {
                    "question": "What challenges have you faced in your career?",
                    "speaker": "interviewer", 
                    "type": "behavioral"
                }
            ],
            "interviewee": [
                {
                    "question": "Могу ли я задать вопрос о команде?",
                    "speaker": "interviewee",
                    "type": "general"
                }
            ],
            "unknown": []
        },
        "by_type": {
            "technical": [
                {
                    "question": "Расскажите о вашем опыте с Python",
                    "speaker": "interviewer",
                    "type": "technical"
                }
            ],
            "behavioral": [
                {
                    "question": "What challenges have you faced in your career?",
                    "speaker": "interviewer",
                    "type": "behavioral"
                }
            ],
            "general": [
                {
                    "question": "Могу ли я задать вопрос о команде?",
                    "speaker": "interviewee",
                    "type": "general"
                }
            ]
        },
        "all_questions": [
            {
                "question": "Расскажите о вашем опыте с Python",
                "speaker": "interviewer",
                "type": "technical"
            },
            {
                "question": "What challenges have you faced in your career?",
                "speaker": "interviewer",
                "type": "behavioral"
            },
            {
                "question": "Могу ли я задать вопрос о команде?",
                "speaker": "interviewee", 
                "type": "general"
            }
        ]
    }
    
    import json
    print("Example questions.json content:")
    print(json.dumps(example_question, ensure_ascii=False, indent=2))


def demo_requirements():
    """Show system requirements and setup."""
    print("\n=== Requirements Demo ===")
    
    print("System Requirements:")
    print("✅ Python 3.8+")
    print("✅ macOS (optimized for M4 MacBook Pro)")
    print("✅ Ollama installed and running")
    print("✅ FFmpeg for video processing")
    print()
    print("Python Dependencies (from requirements.txt):")
    print("- openai-whisper >= 20231117")
    print("- ollama >= 0.2.0") 
    print("- tqdm >= 4.65.0")
    print("- moviepy >= 1.0.3")
    print("- pathlib")
    print("- typing-extensions >= 4.5.0")
    print()
    print("Installation Commands:")
    print("1. pip install -r requirements.txt")
    print("2. brew install ollama")
    print("3. brew install ffmpeg")
    print("4. ollama serve  # Start Ollama service")
    print("5. ollama pull llama3.1:8b  # Download model")


def main():
    """Run all demonstrations."""
    print("🎬 VideoProcessor Demo Script")
    print("=" * 50)
    
    # Set up logging to show info messages
    logging.basicConfig(level=logging.INFO)
    
    try:
        demo_basic_usage()
        demo_custom_settings()
        demo_file_structure()
        demo_question_format()
        demo_requirements()
        
        print("\n" + "=" * 50)
        print("Demo completed! Ready to process your videos.")
        print("Run: python video_processor.py")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nDemo error: {e}")


if __name__ == "__main__":
    main()