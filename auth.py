
def verify_CSRF(incoming_csrf_token, session_csrf_token):
    return incoming_csrf_token == session_csrf_token


