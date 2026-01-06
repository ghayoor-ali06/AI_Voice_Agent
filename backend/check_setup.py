#!/usr/bin/env python3
"""
Setup verification script for AI Voice Agent backend.
Run this to check if everything is configured correctly.
"""
import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.9+)")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print("\n📦 Checking dependencies...")
    required = [
        "fastapi",
        "uvicorn",
        "websockets",
        "pydantic",
        "pydantic_settings",
        "httpx",
        "numpy",
        "pytz"
    ]

    all_installed = True
    for package in required:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (not installed)")
            all_installed = False

    return all_installed


def check_env_file():
    """Check if .env file exists and has required keys."""
    print("\n⚙️  Checking environment configuration...")

    env_path = Path(".env")
    if not env_path.exists():
        print("   ❌ .env file not found")
        print("   💡 Run: cp .env.example .env")
        return False

    print("   ✅ .env file exists")

    # Check for required keys
    with open(env_path) as f:
        content = f.read()

    has_api_key = "OPENAI_API_KEY=" in content and "your_openai_api_key_here" not in content
    has_serper = "SERPER_API_KEY=" in content

    if has_api_key:
        print("   ✅ OPENAI_API_KEY is configured")
    else:
        print("   ⚠️  OPENAI_API_KEY not configured or still has placeholder value")
        print("   💡 Edit .env and add your OpenAI API key")

    if has_serper and "your_serper_api_key_here" not in content:
        print("   ✅ SERPER_API_KEY is configured (optional)")
    else:
        print("   ℹ️  SERPER_API_KEY not configured (optional - will use DuckDuckGo)")

    return has_api_key


def check_project_structure():
    """Check if all required files exist."""
    print("\n📁 Checking project structure...")

    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/websocket/manager.py",
        "app/websocket/handlers.py",
        "app/openai_client/realtime_client.py",
        "app/openai_client/session_manager.py",
        "app/openai_client/prompts.py",
        "app/tools/base.py",
        "app/tools/registry.py",
        "app/tools/web_search.py",
        "app/audio/encoder.py",
        "app/audio/processor.py",
        "app/utils/logger.py",
        "app/utils/exceptions.py",
    ]

    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            all_exist = False

    return all_exist


def test_import():
    """Try importing the main app."""
    print("\n🔧 Testing application import...")
    try:
        from app.main import app
        print("   ✅ Application imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("   AI Voice Agent - Setup Verification")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version()),
        ("Dependencies", check_dependencies()),
        ("Environment Config", check_env_file()),
        ("Project Structure", check_project_structure()),
        ("Application Import", test_import()),
    ]

    print("\n" + "=" * 60)
    print("   Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("🎉 All checks passed! You're ready to run the server.")
        print("\nTo start the server, run:")
        print("   python -m app.main")
        print("\nOr:")
        print("   uvicorn app.main:app --reload")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor help, see:")
        print("   - SETUP.md for setup instructions")
        print("   - README.md for detailed documentation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
