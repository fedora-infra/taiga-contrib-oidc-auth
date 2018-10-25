### Token refresh

Ref: https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html#validate-id-tokens-by-renewing-them

Subclass mozilla_django_oidc.middleware.SessionRefresh to raise
taiga.base.exceptions.NotAuthenticated when the token is no longer valid. Try
to get a new token before we do that. If that works, redirect to the login page
to store the new token in the UI. Make sure the front auth plugin can handle
that case.
