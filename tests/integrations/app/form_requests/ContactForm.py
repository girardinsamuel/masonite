from src.masonite.validation import Form


class ContactForm(Form):

    # redirect_route = "welcome"

    def authorize(self):
        return True

    def rules(self):
        return {"name": "required", "email": "required|email"}
