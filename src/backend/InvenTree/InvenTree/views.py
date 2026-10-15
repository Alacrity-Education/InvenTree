"""Various Views which provide extra functionality over base Django Views.

In particular these views provide base functionality for rendering Django forms
as JSON objects and passing them to modal forms (using jQuery / bootstrap).
"""

from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic.base import RedirectView


class AccountLoginRedirectView(RedirectView):
    """Redirect the legacy 'accounts/login/' URL to the frontend login.

    Anything built on LoginRequiredMixin (the OAuth2 authorize view, for
    example) sends anonymous browsers here with a 'next' parameter. Only a
    same-origin 'next' is forwarded; every other parameter (such as the
    legacy ?login=&password= arguments) is dropped.
    """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """The frontend base URL, with a validated 'next' when one was given."""
        url = f'/{settings.FRONTEND_URL_BASE}'
        next_url = self.request.GET.get('next')

        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            url = f'{url}?{urlencode({"next": next_url})}'

        return url


def auth_request(request):
    """Simple 'auth' endpoint used to determine if the user is authenticated.

    Useful for (for example) redirecting authentication requests through django's permission framework.
    """
    if (
        not request.user
        or not request.user.is_authenticated
        or not request.user.is_active
    ):
        # This is very unlikely to be reached, as the middleware stack should intercept unauthenticated requests
        return HttpResponse(status=403)  # pragma: no cover

    # User is authenticated and active
    return HttpResponse(status=200)
