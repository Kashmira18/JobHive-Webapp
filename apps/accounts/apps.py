from django.apps import AppConfig
from django.conf import settings
from django.db import OperationalError, ProgrammingError
from django.db.models.signals import post_migrate
import logging

logger = logging.getLogger(__name__)


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        from django.apps import apps

        post_migrate.connect(
            ensure_google_social_app,
            sender=apps.get_app_config("socialaccount"),
            dispatch_uid="ensure_google_social_app",
        )


def ensure_google_social_app(sender, **kwargs):
    client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
    client_secret = getattr(settings, "GOOGLE_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        logger.warning("Google OAuth is not configured: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is missing.")
        return

    try:
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp

        site, _ = Site.objects.get_or_create(
            id=settings.SITE_ID,
            defaults={"domain": "localhost", "name": "localhost"},
        )
        app, created = SocialApp.objects.get_or_create(
            provider="google",
            defaults={"name": "Google", "client_id": client_id, "secret": client_secret},
        )
        if not created and (app.client_id != client_id or app.secret != client_secret):
            app.client_id = client_id
            app.secret = client_secret
            app.save(update_fields=["client_id", "secret"])
        app.sites.add(site)
    except (OperationalError, ProgrammingError, RuntimeError) as exc:
        logger.warning("Google OAuth SocialApp setup skipped until migrations are ready: %s", exc)
