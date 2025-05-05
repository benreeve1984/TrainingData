# Garmin Activities Exporter

A Vercel-hosted service that exports Garmin Connect activities to a static JSON file.

## Features

- Logs in to Garmin Connect using the garminconnect Python package
- Fetches up to 2000 activities in a single request
- Exports them to a static JSON file with schema version and timestamp
- Runs once per day at 20:00 UTC via Vercel Cron
- Serves training.json as a static file cached on Vercel's edge

## Setup

1. Clone this repository
2. Link to your Vercel account: `vercel link`
3. Add environment variables to Vercel:
   - `GARMIN_EMAIL`: Your Garmin Connect email
   - `GARMIN_PASSWORD`: Your Garmin Connect password
4. Deploy to Vercel: `vercel deploy --prod`

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest ruff

# Set environment variables
export GARMIN_EMAIL=your_email@example.com
export GARMIN_PASSWORD=your_password

# Run tests
pytest -q

# Start local development server
vercel dev
```

## API

The exported data is available at `/training.json` and follows this schema:

```json
{
  "schema_version": 1,
  "exported_at": "2023-06-14T20:00:00Z",
  "activities": [
    // Array of Garmin Connect activities
  ]
}
``` 