#!/usr/bin/env python3
"""
Video Question Generator

A script that processes video files in the current directory to:
1. Transcribe audio using OpenAI Whisper (supports Russian/English)
2. Generate questions from transcripts using Ollama
3. Identify speaker roles (interviewer vs interviewee)
4. Save organized output in transcribed/ and questions/ folders

Author: AI Assistant
Requirements: See requirements.txt
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
import re

# Third-party imports
import whisper
import ollama
from tqdm import tqdm
from moviepy.editor import VideoFileClip


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_processor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Main class for processing videos and generating questions.
    
    Handles video transcription using Whisper and question generation 
    using Ollama with support for Russian and English languages.
    """
    
    # Supported video file extensions
    SUPPORTED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', 
                           '.webm', '.m4v', '.3gp', '.ogv'}
    
    # Ollama model for question generation (balanced for M4 MacBook Pro)
    OLLAMA_MODEL = "llama3.1:8b"
    
    # Maximum tokens per chunk for Ollama processing
    MAX_CHUNK_TOKENS = 3000
    
    def __init__(self, working_directory: str = "."):
        """
        Initialize the VideoProcessor.
        
        Parameters:
        working_directory (str): Directory to process videos from
        """
        self.working_dir = Path(working_directory).resolve()
        self.transcribed_dir = self.working_dir / "transcribed"
        self.questions_dir = self.working_dir / "questions"
        
        # Create output directories
        self.transcribed_dir.mkdir(exist_ok=True)
        self.questions_dir.mkdir(exist_ok=True)
        
        # Initialize Whisper model
        logger.info("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        
        # Check Ollama availability
        self._check_ollama_model()
    
    def _check_ollama_model(self) -> None:
        """Check if Ollama model is available and pull if necessary."""
        try:
            # Check if model exists
            models = ollama.list()
            model_names = [model['name'] for model in models.get('models', [])]
            
            if self.OLLAMA_MODEL not in model_names:
                logger.info(f"Pulling Ollama model: {self.OLLAMA_MODEL}")
                ollama.pull(self.OLLAMA_MODEL)
                logger.info("Model pulled successfully")
            else:
                logger.info(f"Ollama model {self.OLLAMA_MODEL} is available")
                
        except Exception as e:
            logger.error(f"Error checking Ollama model: {e}")
            raise RuntimeError(
                f"Failed to initialize Ollama model {self.OLLAMA_MODEL}. "
                "Please ensure Ollama is installed and running."
            )
    
    def find_video_files(self) -> List[Path]:
        """
        Find all video files in the working directory.
        
        Returns:
        List[Path]: List of video file paths
        """
        video_files = []
        
        for file_path in self.working_dir.iterdir():
            if (file_path.is_file() and 
                file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS):
                video_files.append(file_path)
        
        logger.info(f"Found {len(video_files)} video files")
        return sorted(video_files)
    
    def transcribe_video(self, video_path: Path) -> str:
        """
        Transcribe a video file using Whisper.
        
        Parameters:
        video_path (Path): Path to the video file
        
        Returns:
        str: Transcribed text
        """
        logger.info(f"Transcribing: {video_path.name}")
        
        try:
            # Extract audio from video
            with VideoFileClip(str(video_path)) as video:
                audio_path = video_path.with_suffix('.wav')
                video.audio.write_audiofile(
                    str(audio_path), 
                    verbose=False, 
                    logger=None
                )
            
            # Transcribe with Whisper
            # Using 'auto' for automatic language detection
            with tqdm(desc=f"Transcribing {video_path.name}", unit="s") as pbar:
                result = self.whisper_model.transcribe(
                    str(audio_path),
                    language=None,  # Auto-detect language
                    task="transcribe",
                    verbose=False
                )
                pbar.update(1)
            
            # Clean up temporary audio file
            audio_path.unlink(missing_ok=True)
            
            transcript = result['text'].strip()
            logger.info(f"Transcription completed for {video_path.name}")
            
            return transcript
            
        except Exception as e:
            logger.error(f"Error transcribing {video_path.name}: {e}")
            raise
    
    def save_transcript(self, video_path: Path, transcript: str) -> Path:
        """
        Save transcript to the transcribed directory.
        
        Parameters:
        video_path (Path): Original video file path
        transcript (str): Transcribed text
        
        Returns:
        Path: Path to saved transcript file
        """
        transcript_file = (
            self.transcribed_dir / f"{video_path.stem}_transcript.txt"
        )
        
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        logger.info(f"Transcript saved: {transcript_file.name}")
        return transcript_file
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks suitable for Ollama processing.
        
        Parameters:
        text (str): Text to chunk
        
        Returns:
        List[str]: List of text chunks
        """
        # Simple chunking by approximate token count
        # Roughly 4 characters per token
        chars_per_chunk = self.MAX_CHUNK_TOKENS * 4
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > chars_per_chunk and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def generate_questions_from_chunk(self, text_chunk: str) -> List[Dict[str, str]]:
        """
        Generate questions from a text chunk using Ollama.
        
        Parameters:
        text_chunk (str): Text chunk to process
        
        Returns:
        List[Dict[str, str]]: List of questions with metadata
        """
        prompt = """
Analyze the following transcript and extract all questions that were asked.
For each question, identify:
1. The exact question text
2. Whether it was asked by an interviewer or interviewee
3. The type of question (technical, behavioral, general)

Return the result as a JSON array where each item has:
- "question": the exact question text
- "speaker": "interviewer" or "interviewee" 
- "type": "technical", "behavioral", or "general"

Transcript:
{text}

Please analyze both Russian and English text appropriately.
"""
        
        try:
            response = ollama.generate(
                model=self.OLLAMA_MODEL,
                prompt=prompt.format(text=text_chunk),
                stream=False
            )
            
            # Try to parse JSON response
            response_text = response['response'].strip()
            
            # Extract JSON from response if it's wrapped in other text
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
                try:
                    questions = json.loads(json_text)
                    return questions if isinstance(questions, list) else []
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response from Ollama")
                    return []
            
            # Fallback: parse manually if JSON parsing fails
            return self._parse_questions_manually(response_text)
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return []
    
    def _parse_questions_manually(self, response_text: str) -> List[Dict[str, str]]:
        """
        Manually parse questions if JSON parsing fails.
        
        Parameters:
        response_text (str): Raw response text
        
        Returns:
        List[Dict[str, str]]: Parsed questions
        """
        questions = []
        lines = response_text.split('\n')
        
        current_question = {}
        for line in lines:
            line = line.strip()
            if '?' in line and len(line) > 10:  # Likely a question
                if current_question:
                    questions.append(current_question)
                current_question = {
                    'question': line,
                    'speaker': 'unknown',
                    'type': 'general'
                }
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def generate_questions(self, transcript: str) -> List[Dict[str, str]]:
        """
        Generate questions from the full transcript.
        
        Parameters:
        transcript (str): Full transcript text
        
        Returns:
        List[Dict[str, str]]: All questions found
        """
        logger.info("Generating questions from transcript...")
        
        chunks = self.chunk_text(transcript)
        all_questions = []
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {i}/{len(chunks)}")
            questions = self.generate_questions_from_chunk(chunk)
            all_questions.extend(questions)
        
        logger.info(f"Generated {len(all_questions)} questions")
        return all_questions
    
    def save_questions(self, video_path: Path, questions: List[Dict[str, str]]) -> Path:
        """
        Save questions to the questions directory.
        
        Parameters:
        video_path (Path): Original video file path
        questions (List[Dict[str, str]]): Questions to save
        
        Returns:
        Path: Path to saved questions file
        """
        questions_file = (
            self.questions_dir / f"{video_path.stem}_questions.json"
        )
        
        # Organize questions by speaker and type
        organized_questions = {
            'video_name': video_path.name,
            'total_questions': len(questions),
            'by_speaker': {
                'interviewer': [],
                'interviewee': [],
                'unknown': []
            },
            'by_type': {
                'technical': [],
                'behavioral': [],
                'general': []
            },
            'all_questions': questions
        }
        
        # Categorize questions
        for question in questions:
            speaker = question.get('speaker', 'unknown')
            question_type = question.get('type', 'general')
            
            organized_questions['by_speaker'][speaker].append(question)
            organized_questions['by_type'][question_type].append(question)
        
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(organized_questions, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Questions saved: {questions_file.name}")
        return questions_file
    
    def process_video(self, video_path: Path) -> Tuple[Path, Path]:
        """
        Process a single video file completely.
        
        Parameters:
        video_path (Path): Path to video file
        
        Returns:
        Tuple[Path, Path]: Paths to transcript and questions files
        """
        logger.info(f"Processing video: {video_path.name}")
        
        try:
            # Transcribe video
            transcript = self.transcribe_video(video_path)
            transcript_file = self.save_transcript(video_path, transcript)
            
            # Generate questions
            questions = self.generate_questions(transcript)
            questions_file = self.save_questions(video_path, questions)
            
            logger.info(f"Completed processing: {video_path.name}")
            return transcript_file, questions_file
            
        except Exception as e:
            logger.error(f"Failed to process {video_path.name}: {e}")
            raise
    
    def process_all_videos(self) -> None:
        """Process all video files in the working directory."""
        video_files = self.find_video_files()
        
        if not video_files:
            logger.info("No video files found in the current directory")
            return
        
        logger.info(f"Starting to process {len(video_files)} video files")
        
        for video_file in video_files:
            try:
                self.process_video(video_file)
            except Exception as e:
                logger.error(f"Skipping {video_file.name} due to error: {e}")
                continue
        
        logger.info("Completed processing all videos")


def main():
    """Main entry point for the script."""
    try:
        processor = VideoProcessor()
        processor.process_all_videos()
        
        print("\n" + "="*50)
        print("Video processing completed successfully!")
        print(f"Transcripts saved in: {processor.transcribed_dir}")
        print(f"Questions saved in: {processor.questions_dir}")
        print("="*50)
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()