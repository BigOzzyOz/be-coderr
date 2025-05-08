from rest_framework.test import APIClient


class JSONAPIClient(APIClient):
    """APIClient that defaults to JSON format for requests."""

    def post(self, path, data=None, format="json", content_type=None, follow=False, **extra):
        """Send POST request with JSON as default format."""
        if content_type is None:
            format = format or "json"
        return super().post(path, data, format=format, content_type=content_type, follow=follow, **extra)

    def put(self, path, data=None, format="json", content_type=None, follow=False, **extra):
        """Send PUT request with JSON as default format."""
        if content_type is None:
            format = format or "json"
        return super().put(path, data, format=format, content_type=content_type, follow=follow, **extra)

    def patch(self, path, data=None, format="json", content_type=None, follow=False, **extra):
        """Send PATCH request with JSON as default format."""
        if content_type is None:
            format = format or "json"
        return super().patch(path, data, format=format, content_type=content_type, follow=follow, **extra)
