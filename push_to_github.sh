#!/bin/bash

# Script to push AI Voice Agent to GitHub
# Repository: https://github.com/ghayoor-ali06/AI_Voice_Agent.git

echo "=========================================="
echo "  Pushing AI Voice Agent to GitHub"
echo "=========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed."
    echo "Please install git first:"
    echo "   sudo apt-get update && sudo apt-get install -y git"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Navigate to project directory
cd "/home/ghayoor-ali/Desktop/voice agents"

# Initialize git repository if not already initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already initialized"
fi
echo ""

# Configure git user (if not already configured)
if [ -z "$(git config user.name)" ]; then
    echo "⚙️  Configuring git user..."
    read -p "Enter your name: " git_name
    read -p "Enter your email: " git_email
    git config user.name "$git_name"
    git config user.email "$git_email"
    echo "✅ Git user configured"
else
    echo "✅ Git user already configured as: $(git config user.name) <$(git config user.email)>"
fi
echo ""

# Add remote if not already added
if ! git remote | grep -q origin; then
    echo "🔗 Adding remote repository..."
    git remote add origin https://github.com/ghayoor-ali06/AI_Voice_Agent.git
    echo "✅ Remote added"
else
    echo "✅ Remote already added"
    # Update remote URL to make sure it's correct
    git remote set-url origin https://github.com/ghayoor-ali06/AI_Voice_Agent.git
fi
echo ""

# Create .env file if it doesn't exist (but don't commit it)
if [ ! -f backend/.env ]; then
    echo "⚠️  Warning: backend/.env file not found"
    echo "   This file is required but won't be committed (it's in .gitignore)"
    echo "   Make sure to create it from backend/.env.example after cloning"
fi
echo ""

# Stage all files
echo "📝 Staging files..."
git add .
echo "✅ Files staged"
echo ""

# Show status
echo "📊 Git status:"
git status --short
echo ""

# Commit
echo "💾 Creating commit..."
COMMIT_MSG="Initial commit: Complete AI Voice Agent implementation

Features:
- FastAPI backend with WebSocket support
- OpenAI GPT-4o Realtime API integration
- Web search tool (Serper API + DuckDuckGo fallback)
- Real-time voice conversations with interruption handling
- Clean, production-ready architecture
- Single HTML file frontend with audio visualizer
- Comprehensive documentation

Tech stack:
- Backend: Python, FastAPI, aiohttp
- Frontend: Vanilla JavaScript, Web Audio API
- AI: OpenAI GPT-4o Realtime API
- Tools: Web search (Serper/DuckDuckGo)

🤖 Generated with Claude Code"

git commit -m "$COMMIT_MSG"
echo "✅ Commit created"
echo ""

# Push to GitHub
echo "🚀 Pushing to GitHub..."
echo "   Repository: https://github.com/ghayoor-ali06/AI_Voice_Agent.git"
echo ""

# Try to push
if git push -u origin main 2>/dev/null; then
    echo "✅ Successfully pushed to main branch!"
elif git push -u origin master 2>/dev/null; then
    echo "✅ Successfully pushed to master branch!"
else
    echo "⚠️  Push failed. Trying to set upstream..."

    # Check current branch
    CURRENT_BRANCH=$(git branch --show-current)

    # Rename to main if needed
    if [ "$CURRENT_BRANCH" != "main" ]; then
        echo "📝 Renaming branch to 'main'..."
        git branch -M main
    fi

    # Force push (for first push to empty repo)
    echo "🚀 Pushing to origin/main..."
    git push -u origin main --force

    if [ $? -eq 0 ]; then
        echo "✅ Successfully pushed!"
    else
        echo "❌ Push failed. You may need to:"
        echo "   1. Check your GitHub credentials"
        echo "   2. Ensure the repository exists: https://github.com/ghayoor-ali06/AI_Voice_Agent.git"
        echo "   3. Try pushing manually: git push -u origin main"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "  ✅ Success!"
echo "=========================================="
echo ""
echo "Your code is now on GitHub:"
echo "🔗 https://github.com/ghayoor-ali06/AI_Voice_Agent"
echo ""
echo "Next steps:"
echo "1. Add a profile picture and description to your repo"
echo "2. Add topics/tags for better discoverability"
echo "3. Consider adding a LICENSE file"
echo "4. Share your project!"
echo ""
