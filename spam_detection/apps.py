from django.apps import AppConfig


class SpamDetectionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "spam_detection"

    def ready(self):
        import spam_detection.signals
