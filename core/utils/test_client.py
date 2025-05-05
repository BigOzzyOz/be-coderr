from rest_framework.test import APIClient


class JSONAPIClient(APIClient):
    def post(self, path, data=None, format="json", content_type=None, follow=False, **extra):
        if content_type is None:
            format = format or "json"
        return super().post(path, data, format=format, content_type=content_type, follow=follow, **extra)

    def put(self, path, data=None, format="json", content_type=None, follow=False, **extra):
        if content_type is None:
            format = format or "json"
        return super().put(path, data, format=format, content_type=content_type, follow=follow, **extra)

    def patch(self, path, data=None, format="json", content_type=None, follow=False, **extra):
        if content_type is None:
            format = format or "json"
        return super().patch(path, data, format=format, content_type=content_type, follow=follow, **extra)
