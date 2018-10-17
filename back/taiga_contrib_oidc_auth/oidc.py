# Copyright (C) 2018 Aurelien Bompard <aurelien@bompard.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unicodedata

from django.apps import apps
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from taiga.auth.services import send_register_email
from taiga.auth.signals import user_registered as user_registered_signal


# TODO: check groups? https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html#advanced-user-verification-based-on-their-claims


class TaigaOIDCAuthenticationBackend(OIDCAuthenticationBackend):

    AUTHDATA_KEY = "oidc"

    def filter_users_by_claims(self, claims):
        email = claims.get("email")
        if not email:
            return self.UserModel.objects.none()

        AuthData = apps.get_model("users", "AuthData")
        try:
            auth_data = AuthData.objects.filter(
                key=self.AUTHDATA_KEY, user__email__iexact=email
            )
            return [ad.user for ad in auth_data]

        except AuthData.DoesNotExist:
            return self.UserModel.objects.none()

    def get_username(self, claims):
        nickname = claims.get("nickname")
        if not nickname:
            return super(TaigaOIDCAuthenticationBackend, self).get_username(claims)
        return unicodedata.normalize("NFKC", nickname)[:150]

    def create_user(self, claims):
        email = claims.get("email")
        if not email:
            return None

        username = self.get_username(claims)
        full_name = claims.get("name", username)

        AuthData = apps.get_model("users", "AuthData")
        try:
            # User association exist?
            auth_data = AuthData.objects.get(key=self.AUTHDATA_KEY, value=username)
            user = auth_data.user
        except AuthData.DoesNotExist:
            try:
                # Is a user with the same email?
                user = self.UserModel.objects.get(email=email)
                AuthData.objects.create(
                    user=user, key=self.AUTHDATA_KEY, value=username, extra={}
                )
            except self.UserModel.DoesNotExist:
                # Create a new user
                user = self.UserModel.objects.create(
                    email=email, username=username, full_name=full_name
                )
                AuthData.objects.create(
                    user=user, key=self.AUTHDATA_KEY, value=username, extra={}
                )

                send_register_email(user)
                user_registered_signal.send(sender=self.UserModel, user=user)

        return user

    def update_user(self, user, claims):
        try:
            user.full_name = claims["name"]
        except KeyError:
            pass
        else:
            user.save()
        return user
