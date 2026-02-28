"""
Entry point for local development.
Run with:  python main.py
Or with:   uvicorn app.main:app --reload
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,          # auto-reload on file changes during development
    )
