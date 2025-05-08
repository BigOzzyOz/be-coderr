from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """AppConfig for auth_app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_app"

    def ready(self):
        """Import signals when app is ready."""
        import auth_app.api.signals
