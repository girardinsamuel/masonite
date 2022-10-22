from src.masonite.facades import Url
from src.masonite.exceptions import ValidationException
from src.masonite.exceptions import AuthorizationException
from .ValidatorTwo import Validator


class Form:

    redirect = None
    redirect_route = None

    def __init__(self, request=None):
        self.request = None
        self.validator = None

    def set_request(self, request):
        self.request = request
        return self

    def rules(self):
        return {}

    def get_validator(self):
        if self.validator:
            return self.validator
        else:
            validator = Validator(self.request.all(), self.rules())

        self.validator = validator
        return self.validator

    def validate_when_resolved(self):
        validator = self.get_validator()

        # check authorization
        if not self.authorize():
            raise AuthorizationException()

        # validate request
        validator.validate()

        # continue depending on validation status
        if validator.invalid():
            raise ValidationException(validator, redirect_url=self.get_redirect_url())
        return self

    def validated(self):
        """Get validated data"""
        validator = self.get_validator()
        return validator.validated()

    def get_redirect_url(self):
        if self.redirect:
            return Url.url(self.redirect)
        elif self.redirect_route:
            return Url.route(self.redirect_route)
        else:
            return None

    def authorize(self):
        return True
