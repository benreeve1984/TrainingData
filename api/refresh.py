import json
import os
import sys
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

            # Log environment information for debugging
            debug_info = {
                "env_vars": {k: v for k, v in os.environ.items() if not k.startswith("AWS_") and not "PASSWORD" in k and not "SECRET" in k},
                "cwd": os.getcwd(),
                "path_exists": {}
            }
            
            # Try multiple common Vercel public paths
            possible_paths = [
                "./public/training.json",
                "/vercel/output/static/training.json",
                "/vercel/path0/public/training.json",
                "/var/task/public/training.json",
                os.path.join(os.getcwd(), "public", "training.json"),
                Path(os.environ.get("VERCEL_OUTPUT_DIR", "/tmp")) / "static" / "training.json",
                Path(os.environ.get("VERCEL_OUTPUT_DIR", "/tmp")) / "public" / "training.json",
                "/tmp/training.json"
            ]
            
            # Check which paths exist
            for path_str in possible_paths:
                path = Path(path_str)
                parent_dir = path.parent
                debug_info["path_exists"][str(path)] = os.path.exists(path)
                debug_info["path_exists"][f"{parent_dir} (dir)"] = os.path.exists(parent_dir)
                
                # Create directory if it doesn't exist
                if not os.path.exists(parent_dir) and "tmp" not in str(parent_dir).lower():
                    try:
                        os.makedirs(parent_dir, exist_ok=True)
                        debug_info["path_exists"][f"{parent_dir} (created)"] = True
                    except Exception as e:
                        debug_info["path_exists"][f"{parent_dir} (error)"] = str(e)
            
            # Write to all possible paths to maximize chances of success
            written_paths = []
            for path_str in possible_paths:
                try:
                    with open(path_str, "w") as f:
                        json.dump(payload, f, indent=2)
                    written_paths.append(path_str)
                except Exception as e:
                    debug_info[f"error_{path_str}"] = str(e)
            
            # Try to write to the public directory relative to the current directory
            try:
                # Create public directory in project root
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                public_dir = os.path.join(project_root, "public")
                if not os.path.exists(public_dir):
                    os.makedirs(public_dir, exist_ok=True)
                
                # Write to public/training.json in project root
                project_path = os.path.join(public_dir, "training.json")
                with open(project_path, "w") as f:
                    json.dump(payload, f, indent=2)
                written_paths.append(project_path)
            except Exception as e:
                debug_info["error_project_path"] = str(e)

            # Return success response with debug info
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            response = {
                "message": f"Wrote {len(activities)} activities",
                "written_paths": written_paths,
                "debug_info": debug_info
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode()) 