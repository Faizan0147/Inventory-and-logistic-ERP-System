"""
Entry point for local development.
Run with:  python main.py
Or with:   uvicorn app.main:app --reload

Flags:
  --ngrok   Start an ngrok tunnel for external access
"""

import sys
import uvicorn


def start_ngrok(port: int) -> str:
    """Open an ngrok tunnel and return the public URL."""
    from pyngrok import ngrok, conf
    from app.config import settings

    if not settings.NGROK_AUTHTOKEN:
        print("ERROR: Set NGROK_AUTHTOKEN in your .env file.")
        print("Get your token at https://dashboard.ngrok.com/get-started/your-authtoken")
        sys.exit(1)

    conf.get_default().auth_token = settings.NGROK_AUTHTOKEN

    kwargs = {"bind_tls": True}  # HTTPS only
    if settings.NGROK_DOMAIN:
        kwargs["hostname"] = settings.NGROK_DOMAIN

    tunnel = ngrok.connect(port, **kwargs)
    public_url = tunnel.public_url

    print("\n" + "=" * 60)
    print("ngrok tunnel active")
    print(f"Public URL : {public_url}")
    print(f"API docs   : {public_url}/docs")
    print("=" * 60 + "\n")

    return public_url


if __name__ == "__main__":

    port = 8000
    use_ngrok = "--ngrok" in sys.argv

    if use_ngrok:
        start_ngrok(port)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=not use_ngrok,  # reload conflicts with ngrok
    )