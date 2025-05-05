import json
import os
from datetime import datetime
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

            # For plain text endpoint
            if "/training.txt" in self.path:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.send_header('Cache-Control', 'public, max-age=0, s-maxage=3600, stale-while-revalidate')
                self.end_headers()
                
                # Format the JSON as a readable plain text
                plain_text = f"Schema Version: {payload['schema_version']}\n"
                plain_text += f"Exported At: {payload['exported_at']}\n"
                plain_text += f"Total Activities: {len(activities)}\n\n"
                
                # Add summary of each activity
                for i, activity in enumerate(activities[:100]):  # Limit to first 100 to avoid oversized responses
                    plain_text += f"Activity {i+1}:\n"
                    plain_text += f"  Type: {activity.get('activityType', {}).get('typeKey', 'Unknown')}\n"
                    plain_text += f"  Start: {activity.get('startTimeLocal', 'Unknown')}\n"
                    plain_text += f"  Duration: {activity.get('duration', 0)} seconds\n"
                    plain_text += f"  Distance: {activity.get('distance', 0)} meters\n"
                    plain_text += f"  Calories: {activity.get('calories', 0)}\n"
                    plain_text += "\n"
                
                if len(activities) > 100:
                    plain_text += f"... and {len(activities) - 100} more activities (truncated for size)"
                    
                self.wfile.write(plain_text.encode())
                return

            # For direct fetch, just return JSON data
            if "/training.json" in self.path:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Cache-Control', 'public, max-age=0, s-maxage=3600, stale-while-revalidate')
                self.end_headers()
                self.wfile.write(json.dumps(payload, indent=2).encode())
                return

            # For function invocation (without training.json in path), return success message with stats
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": f"Wrote {len(activities)} activities",
                "activity_count": len(activities),
                "last_sync": datetime.utcnow().isoformat() + "Z"
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode()) 