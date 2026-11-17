import sys
import uvicorn
from app import app

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    print(f"Starting BioCrypt-DNA laboratory workstation on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

