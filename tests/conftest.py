from pathlib import Path
from unittest.mock import patch

import httpx
import pytest


@pytest.fixture(scope="session")
def mock_httpx_transport():
    """Mock transport for httpx that returns test file content"""

    # Dictionary to store specific content overrides for URLs
    content_overrides = {}

    def handler(request):
        url = str(request.url)

        # Check if there's specific content for this URL
        if url in content_overrides:
            return httpx.Response(200, content=content_overrides[url])

        # Otherwise, use the corresponding test file
        filename = request.url.path.split("/")[-1]
        test_file_path = Path("tests/data") / filename

        if test_file_path.exists():
            content = test_file_path.read_bytes()
            return httpx.Response(200, content=content)
        else:
            return httpx.Response(404, content=b"File not found")

    transport = httpx.MockTransport(handler)

    # Expose a method to define specific content overrides
    def mock_http_response_for_url(url, content):
        """Mock a specific HTTP response for a given URL instead of using test file content"""
        content_overrides[url] = content.encode("utf-8") if isinstance(content, str) else content

    # Patch httpx.get pour les tests qui injectent mock_httpx_transport
    with patch("httpx.get") as mock_get:

        def mock_httpx_get(url, **kwargs):
            with httpx.Client(transport=transport) as client:
                # httpx.Client.get() doesn't support raise_for_status, so we ignore it
                kwargs.pop("raise_for_status", None)
                return client.get(url, **kwargs)

        mock_get.side_effect = mock_httpx_get
        # Attach the method to the mock so it's accessible in tests
        mock_get.mock_http_response_for_url = mock_http_response_for_url
        yield mock_get
