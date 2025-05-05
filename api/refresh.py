import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from garminconnect import Garmin


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle serverless function request to refresh Garmin activities."""
    try:
        # Get credentials from environment
        email = os.environ.get("GARMIN_EMAIL")
        password = os.environ.get("GARMIN_PASSWORD")

        if not email or not password:
            return {
                "statusCode": 500,
                "body": "Missing GARMIN_EMAIL or GARMIN_PASSWORD environment variables"
            }

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

        return {
            "statusCode": 200,
            "body": f"Wrote {len(activities)} activities"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        } 