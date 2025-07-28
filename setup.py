#!/usr/bin/env python3
"""
Setup script for VideoProcessor.

This script helps with initial setup and dependency installation.
"""

import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is adequate."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_platform():
    """Check if platform is supported."""
    system = platform.system()
    machine = platform.machine()
    
    print(f"Platform: {system} {machine}")
    
    if system == "Darwin":  # macOS
        print("✅ macOS detected")
        return True
    else:
        print("⚠️  This script is optimized for macOS")
        print("   It may work on other platforms but is untested")
        return True


def run_command(command, description, critical=True):
    """Run a shell command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        if critical:
            return False
        return True


def install_python_dependencies():
    """Install Python dependencies."""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )


def check_homebrew():
    """Check if Homebrew is installed (macOS only)."""
    if platform.system() != "Darwin":
        return True
    
    try:
        subprocess.run(["brew", "--version"], check=True, capture_output=True)
        print("✅ Homebrew is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Homebrew not found")
        print("   Install from: https://brew.sh")
        return False


def install_system_dependencies():
    """Install system dependencies."""
    if platform.system() != "Darwin":
        print("⚠️  System dependency installation only supported on macOS")
        return True
    
    success = True
    
    # Install ffmpeg
    success &= run_command(
        "brew install ffmpeg",
        "Installing ffmpeg",
        critical=False
    )
    
    # Install ollama
    success &= run_command(
        "brew install ollama",
        "Installing Ollama",
        critical=False
    )
    
    return success


def setup_ollama():
    """Set up Ollama and download model."""
    print("\n=== Ollama Setup ===")
    
    # Check if Ollama is running
    try:
        subprocess.run(
            ["ollama", "list"], 
            check=True, 
            capture_output=True
        )
        print("✅ Ollama is running")
    except subprocess.CalledProcessError:
        print("⚠️  Ollama service not running")
        print("   Start with: ollama serve")
        print("   Then run this setup again")
        return False
    except FileNotFoundError:
        print("❌ Ollama not found")
        print("   Install with: brew install ollama")
        return False
    
    # Download model
    return run_command(
        "ollama pull llama3.1:8b",
        "Downloading Ollama model (this may take a while)",
        critical=False
    )


def create_config():
    """Create configuration file from template."""
    config_template = Path("config_template.py")
    config_file = Path("config.py")
    
    if config_file.exists():
        print("✅ config.py already exists")
        return True
    
    if not config_template.exists():
        print("❌ config_template.py not found")
        return False
    
    try:
        config_template.read_text().replace(
            "config_template.py", 
            config_file.name
        )
        config_file.write_text(config_template.read_text())
        print("✅ Created config.py from template")
        return True
    except Exception as e:
        print(f"❌ Failed to create config.py: {e}")
        return False


def run_basic_test():
    """Run basic functionality test."""
    print("\n=== Running Basic Test ===")
    
    try:
        # Test imports
        print("Testing imports...")
        subprocess.run([
            sys.executable, "-c",
            "import whisper; import ollama; import moviepy; print('✅ All imports successful')"
        ], check=True)
        
        # Test video processor compilation
        print("Testing video processor...")
        subprocess.run([
            sys.executable, "-m", "py_compile", "video_processor.py"
        ], check=True)
        
        print("✅ Basic test passed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Basic test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🎬 VideoProcessor Setup Script")
    print("=" * 50)
    
    success = True
    
    # Check requirements
    success &= check_python_version()
    success &= check_platform()
    
    if not success:
        print("\n❌ System requirements not met")
        sys.exit(1)
    
    # Check Homebrew (macOS only)
    if platform.system() == "Darwin":
        if not check_homebrew():
            print("\n⚠️  Install Homebrew first, then run setup again")
            sys.exit(1)
    
    # Install dependencies
    print("\n=== Installing Dependencies ===")
    success &= install_python_dependencies()
    success &= install_system_dependencies()
    
    # Setup Ollama
    success &= setup_ollama()
    
    # Create config
    create_config()
    
    # Run test
    if success:
        run_basic_test()
    
    # Final status
    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Place video files in this directory")
        print("2. Run: python video_processor.py")
        print("3. Check output in transcribed/ and questions/ folders")
    else:
        print("⚠️  Setup completed with some warnings")
        print("Check the messages above and resolve any issues")
    
    print("\nFor help, see README.md")


if __name__ == "__main__":
    main()