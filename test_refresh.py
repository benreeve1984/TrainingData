import os
from unittest.mock import patch, MagicMock

from api.refresh import handler


def test_handler_returns_200():
    """Test that the handler returns a 200 status code."""
    with patch("api.refresh.Garmin") as mock_garmin, \
         patch("api.refresh.json.dump") as mock_dump, \
         patch("builtins.open", MagicMock()), \
         patch.dict(os.environ, {"GARMIN_EMAIL": "test@example.com", "GARMIN_PASSWORD": "password"}):
        
        # Configure mocks
        mock_api = MagicMock()
        mock_api.get_activities.return_value = []
        mock_garmin.return_value = mock_api
        
        # Call handler
        result = handler({})
        
        # Assert status code is 200
        assert result["statusCode"] == 200
        assert "Wrote 0 activities" in result["body"] 