try:
    import fastapi
    import uvicorn
    import jobspy
    import resend

    print("Imports successful!")
except ImportError as e:
    print(f"Import failed: {e}")
