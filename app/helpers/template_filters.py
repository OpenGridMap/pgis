from app import GisApp

@GisApp.template_filter()
def email_to_username(email):
    return email.partition("@")[0][0:6]