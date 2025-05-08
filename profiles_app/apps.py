from django.apps import AppConfig


class ProfilesAppConfig(AppConfig):
    """AppConfig for profiles_app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles_app"

    def ready(self):
        """Import signals when app is ready."""
        import profiles_app.signals
