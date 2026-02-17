#!/usr/bin/env python
"""Start the AutoDev Agent Web UI."""

import sys
import webbrowser
import time
from pathlib import Path

# Ensure we're in the right directory
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main() -> None:
    """Start the web UI server."""
    print("\n" + "=" * 70)
    print("🚀 AutoDev Agent - Web User Interface")
    print("=" * 70 + "\n")

    # Check dependencies
    print("📦 Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✓ FastAPI, Uvicorn, Pydantic installed\n")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("   Run: pip install fastapi uvicorn pydantic\n")
        sys.exit(1)

    # Import our web app
    print("⚙️  Loading application...")
    try:
        from app.web_ui import app
        print("✓ Application loaded\n")
    except Exception as e:
        print(f"✗ Failed to load application: {e}\n")
        sys.exit(1)

    # Print startup message
    print("=" * 70)
    print("🌐 Web Server Details:")
    print("   URL: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("=" * 70)
    print("\n📝 Instructions:")
    print("   1. Configure task settings in the UI")
    print("   2. Click 'Start Task' button")
    print("   3. Watch logs in real-time")
    print("   4. View generated projects")
    print("\n🛑 To stop: Press Ctrl+C\n")

    # Open browser after a short delay
    print("⏳ Starting server (opening browser in 2 seconds)...\n")
    time.sleep(1)

    try:
        webbrowser.open("http://localhost:8000")
        print("✓ Browser opened\n")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Open manually: http://localhost:8000\n")

    # Start server
    print("Server running... Press Ctrl+C to stop\n")
    print("=" * 70 + "\n")

    try:
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("✓ Server stopped cleanly")
        print("=" * 70 + "\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Server error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
