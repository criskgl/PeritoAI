# Installation Guide - macOS

## Quick Fix for "pip: command not found"

On macOS, especially with Homebrew Python installations, you need to use `pip3` instead of `pip`.

## Installation Steps

### Option 1: Direct Installation (Recommended)

```bash
# Navigate to project directory
cd /Users/crisgomezlopez/Projects/peritoAi

# Install dependencies using pip3
pip3 install -r requirements.txt

# Or using python3 -m pip (always works)
python3 -m pip install -r requirements.txt
```

### Option 2: Using Virtual Environment (Best Practice)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Now you can use 'pip' directly (it will use venv's pip)
pip install -r requirements.txt

# To deactivate later
deactivate
```

### Option 3: Add pip3 to PATH (Permanent Fix)

If you want to use `pip` directly, you can create an alias:

```bash
# Add to your ~/.zshrc file
echo 'alias pip="pip3"' >> ~/.zshrc
echo 'alias python="python3"' >> ~/.zshrc

# Reload your shell
source ~/.zshrc
```

## Verify Installation

After installation, verify everything works:

```bash
# Check Python version (should be 3.10+)
python3 --version

# Check pip version
pip3 --version

# Test imports
python3 -c "import streamlit; import fastapi; import chromadb; print('All imports successful!')"
```

## Setting Up Environment Variables

```bash
# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key_here
EOF

# Edit with your actual API key
nano .env
# or
open -e .env
```

## Running the Application

### Streamlit UI
```bash
# Using python3 directly
python3 -m streamlit run app.py

# Or if streamlit is in PATH
streamlit run app.py
```

### FastAPI Server
```bash
# Using python3 directly
python3 main.py

# Or using uvicorn
python3 -m uvicorn main:app --reload
```

## Troubleshooting

### "pip: command not found"
- **Solution**: Use `pip3` or `python3 -m pip` instead
- **Why**: macOS often doesn't have `pip` in PATH, but `pip3` is available

### "python: command not found"
- **Solution**: Use `python3` instead
- **Verify**: Check with `which python3`

### Permission Errors
- **Solution**: Add `--user` flag: `pip3 install --user -r requirements.txt`
- **Better**: Use a virtual environment (Option 2 above)

### Package Installation Errors
- **Solution**: Update pip first: `python3 -m pip install --upgrade pip`
- **Then**: `python3 -m pip install -r requirements.txt`
