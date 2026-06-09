# Local Running Notes

This demo uses only the Python standard library.

## Start

```bash
python3 src/server.py
```

Open:

```text
http://127.0.0.1:8000
```

## Test

```bash
python3 -m unittest discover -s tests
```

## LLM Configuration

If `OPENAI_API_KEY` is not set, the app returns a local fallback answer and marks it for human review.

```bash
export OPENAI_API_KEY=your_key
export OPENAI_BASE_URL=https://api.openai.com/v1
export OPENAI_MODEL=gpt-4.1-mini
python3 src/server.py
```
