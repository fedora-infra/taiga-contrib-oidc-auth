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

from six.moves.urllib.parse import urlencode

from mozilla_django_oidc.views import OIDCAuthenticationCallbackView
from mozilla_django_oidc.utils import import_from_settings
from taiga.auth.services import make_auth_response_data


def _make_login_url(data):
    SITES = import_from_settings(
        "SITES",
        {
            "api": {"domain": "localhost:8000", "scheme": "http", "name": "api"},
            "front": {"domain": "localhost:9001", "scheme": "http", "name": "front"},
        },
    )
    return "{}://{}/login?{}".format(
        SITES["front"]["scheme"], SITES["front"]["domain"], urlencode(data)
    )


class TaigaOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):
    @property
    def success_url(self):
        # Pull the next url from the session or settings--we don't need to
        # sanitize here because it should already have been sanitized.
        next_url = self.request.session.get("oidc_login_next") or "/"
        data = make_auth_response_data(self.user)
        data["type"] = "oidc"
        data["next"] = next_url
        return _make_login_url(data)

    @property
    def failure_url(self):
        data = {
            "type": "oidc",
            "next": self.request.session.get("oidc_login_next") or "/",
            "error": self.request.GET.get("error"),
            "error_description": self.request.GET.get("error_description"),
        }
        return _make_login_url(data)
