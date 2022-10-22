class ValidationExceptionHandler:
    def __init__(self, application):
        self.application = application

    def handle(self, exception):
        response = self.application.make("response")
        request = self.application.make("request")
        errors = exception.get_errors()
        redirect_url = (
            exception.get_redirect_url()
            or request.session.get("_previous.url")
            or request.get_back_path()
        )
        return response.redirect(redirect_url).with_errors(errors).with_input()
