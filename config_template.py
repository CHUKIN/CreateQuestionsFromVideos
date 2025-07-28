# Configuration file for VideoProcessor
# Copy this file to config.py and modify as needed

# Ollama model selection
# Options: llama3.1:8b, mistral:7b, codellama:7b, etc.
OLLAMA_MODEL = "llama3.1:8b"

# Maximum tokens per chunk for Ollama processing
# Adjust based on your model's context window
MAX_CHUNK_TOKENS = 3000

# Whisper model size
# Options: tiny, base, small, medium, large
WHISPER_MODEL = "base"

# Supported video file extensions
SUPPORTED_EXTENSIONS = {
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv',
    '.webm', '.m4v', '.3gp', '.ogv'
}

# Output directory names
TRANSCRIBED_DIR = "transcribed"
QUESTIONS_DIR = "questions"

# Logging configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "video_processor.log"

# Question generation prompt template
QUESTION_PROMPT_TEMPLATE = """
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

# Audio extraction settings
AUDIO_FORMAT = "wav"
AUDIO_TEMP_CLEANUP = True

# Progress bar settings
PROGRESS_BAR_FORMAT = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}"