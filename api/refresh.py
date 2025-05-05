import json
import os
from datetime import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler

from garminconnect import Garmin


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get credentials from environment
            email = os.environ.get("GARMIN_EMAIL")
            password = os.environ.get("GARMIN_PASSWORD")

            if not email or not password:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write("Missing GARMIN_EMAIL or GARMIN_PASSWORD environment variables".encode())
                return

            # Initialize and login to Garmin Connect
            api = Garmin(email, password)
            api.login()

            # Fetch activities (up to 2000)
            activities = api.get_activities(0, 2000)

            # Build payload
            payload = {
                "schema_version": 1,
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "activities": activities
            }

            # Determine where to write the file
            static_dir = Path(os.environ.get("VERCEL_STATIC_FILES", "/tmp"))
            output_path = static_dir / "training.json"

            # Write the JSON file
            with open(output_path, "w") as f:
                json.dump(payload, f, indent=2)

            # Return success response
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Wrote {len(activities)} activities".encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode()) 