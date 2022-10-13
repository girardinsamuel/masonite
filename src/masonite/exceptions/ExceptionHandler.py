from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..foundation import Application

from . import (
    DumpExceptionHandler,
    HttpExceptionHandler,
    ModelNotFoundHandler,
)


class ExceptionHandler:

    ignore = []

    def __init__(self, application: "Application", driver_config=None):
        self.application = application
        self.drivers = {}
        self.driver_config = driver_config or {}
        self.options = {}

    def set_options(self, options):
        self.options = options
        return self

    def add_driver(self, name, driver):
        self.drivers.update({name: driver})

    def set_configuration(self, config):
        self.driver_config = config
        return self

    def get_driver(self, name=None):
        if name is None:
            return self.drivers[self.driver_config.get("default")]
        return self.drivers[name]

    def get_config_options(self, driver=None):
        if driver is None:
            return self.driver_config[self.driver_config.get("default")]

        return self.driver_config.get(driver, {})

    def context(self):
        return {}

    def report(self, exception):
        """Masonite internal logic used to report an exception."""

        if self.should_not_report(exception):
            return

        # fire an event
        self.application.make("event").fire(
            f"masonite.exception.{exception.__class__.__name__}", exception
        )

        # log the exception (TODO in logging PR)
        context = {**self.context(), **exception.get_context()}
        # Log.error(exception.get_message(), context=context)

    def should_not_report(self, exception):
        return exception.__class__ in self.ignore

    def render_for_console(self, exception):
        exceptionite = self.get_driver("exceptionite")
        exceptionite.start(exception)
        return exceptionite.render("terminal")

    def render(self, exception):

        # if an exception handler is registered for this exception, use it instead
        if self.application.has(f"{exception.__class__.__name__}Handler"):
            return self.application.make(
                f"{exception.__class__.__name__}Handler"
            ).handle(exception)

        response = self.application.make("response")
        request = self.application.make("request")
        # handle exception in production
        if not self.application.is_debug():
            # for HTTP error codes (500, 404, 403...) a specific page should be displayed
            # if a renderable exception is raised let it be displayed
            if hasattr(exception, "is_http_exception") or hasattr(
                exception, "get_response"
            ):
                return self.application.make("HttpExceptionHandler").handle(exception)

            # else fallback to an unknown exception that should be displayed as a 500 error
            exception.get_status = lambda: 500
            exception.get_response = lambda: str(exception) or "Unknown error"
            return self.application.make("HttpExceptionHandler").handle(exception)
        else:
            # handle exception in development mode with Exceptionite
            exceptionite = self.get_driver("exceptionite")
            exceptionite.start(exception)
            exceptionite.render("terminal")
            if request.expects_json():
                content = exceptionite.render("json")
            else:
                content = exceptionite.render("web")
            return response.view(content, status=500)

    def enrich_exception(self, exception):
        exceptionite = self.get_driver("exceptionite")
        exceptionite.start(exception)
        stacktrace = exceptionite.stacktrace()
        # add info
        exception.get_namespace = lambda: exceptionite.namespace()
        exception.get_stacktrace = lambda: stacktrace
        exception.get_file = lambda: stacktrace.first().file
        exception.get_lineno = lambda: stacktrace.first().lineno
        if not hasattr(exception, "get_context"):
            exception.get_context = lambda: {}

        return exception

    def handle(self, exception):
        self.enrich_exception(exception)
        try:
            self.report(exception)
        except:
            # if the code above or the user code in custom report() method throw an exception
            # the app will crash and we don't want that, so this ensure that the user won't
            # see a crash here but the handled exception
            pass

        if self.application.is_running_in_console():
            return self.render_for_console(exception)
        else:
            return self.render(exception)

    def register(self):
        self.application.bind(
            "DumpExceptionHandler", DumpExceptionHandler(self.application)
        )
        self.application.bind(
            "HttpExceptionHandler", HttpExceptionHandler(self.application)
        )
        self.application.bind(
            "ModelNotFoundHandler", ModelNotFoundHandler(self.application)
        )
