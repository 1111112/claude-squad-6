#!/bin/bash
# Claude Squad 5 - One-command setup script

set -e  # Exit on error

echo "🚀 Claude Squad 5 - Enterprise-Grade Development Team Simulation"
echo "=============================================================="

# Check Python version
if ! python3 --version &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "⚠️  Warning: Not in a git repository. Some features may be limited."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << EOF
# Claude Squad 5 Dependencies
pyyaml>=6.0
click>=8.0
rich>=13.0
asyncio>=3.4
dataclasses>=0.6
python-dotenv>=0.19
EOF
fi

pip install -q -r requirements.txt

# Create project structure if needed
echo "🏗️  Setting up project structure..."
mkdir -p .claude-squad/{context,logs,metrics}

# Initialize context file
if [ ! -f ".claude-squad/context/project.json" ]; then
    cat > .claude-squad/context/project.json << EOF
{
  "project_name": "$(basename $(pwd))",
  "team_size": 5,
  "initialized": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "tech_stack": [],
  "quality_standards": {
    "test_coverage": 80,
    "mutation_score": 70,
    "max_complexity": 10
  }
}
EOF
fi

# Create CLI symlink
echo "🔗 Creating CLI command..."
chmod +x claude-squad-5/cli.py

# Add to PATH for current session
export PATH="$PATH:$(pwd)/claude-squad-5"

echo "✅ Setup complete!"
echo ""
echo "🎯 Quick Start:"
echo "   claude-squad init              # Initialize for current project"
echo "   claude-squad feature \"...\"     # Start a new feature"
echo "   claude-squad sprint \"...\"      # Run a full sprint"
echo "   claude-squad status            # Check team status"
echo ""
echo "📚 Documentation: claude-squad-5/README.md"