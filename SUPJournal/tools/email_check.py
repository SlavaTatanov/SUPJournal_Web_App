from email_validator import validate_email, EmailUndeliverableError, EmailSyntaxError

def check_email(em: str) -> bool:
    try:
        validate_email(em, check_deliverability=True)
        return True
    except EmailUndeliverableError:
        return False
    except EmailSyntaxError:
        return False