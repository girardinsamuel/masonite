from src.masonite.exceptions import ExceptionHandler


class AppExceptionHandler(ExceptionHandler):

    ignore = []

    def report(self, exception):
        """Here you can do what you want with the exception (before it is processed by Masonite)."""
        super().report(exception)
        import pdb

        pdb.set_trace()

    def context(self):
        base_context = super().context()
        return base_context.update({})

    def register(self):
        """Register here custom exception handlers."""
        pass
