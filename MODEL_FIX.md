# Model Fix Guide

## Issue: Model Not Found Error

Error: `models/gemini-1.5-pro is not found for API version v1beta`  
Error: `models/gemini-pro is not found for API version v1beta`

## Solution

The model name has been changed to **`gemini-2.5-flash-lite`** by default, which is:
- Optimized for cost-efficiency and high throughput
- Supports up to 1M input tokens and 65K output tokens
- Compatible with current API versions
- Ideal for production use

### Available Model Options:

1. **`gemini-2.5-flash-lite`** (Default - Recommended)
   - Cost-efficient and fast
   - High throughput
   - Supports large context windows
   - **Currently used as default**

2. **`gemini-2.5-flash`** (Alternative)
   - Similar to flash-lite but may have different characteristics
   - Check API availability

3. **`gemini-1.5-pro`** (If Available)
   - May require specific API access level
   - More powerful but potentially slower

## How to Change Model

### Option 1: Change in Code

Edit `engine/generator.py` line 25:
```python
model_name: str = "gemini-pro",  # Change to "gemini-1.5-flash" or other
```

### Option 2: Environment Variable (Future Enhancement)

You could add a `GEMINI_MODEL` environment variable to make it configurable without code changes.

## Testing

Try generating a report again with the new default model (`gemini-pro`). If you still get errors, try `gemini-1.5-flash`.
