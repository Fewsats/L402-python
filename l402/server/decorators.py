from functools import wraps
from flask import Response
from .authenticator import Authenticator, InvalidOrMissingL402Header

def require_l402_payment(authenticator: Authenticator, get_price_func):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract the request from kwargs or args as appropriate
            request = kwargs.get('request') if 'request' in kwargs else args[0]
            l402_header = request.headers.get('Authenticate')
            try:
                authenticator.validate_l402_header(l402_header)
                # If we got here, it means we have a valid L402 header
                return f(*args, **kwargs)
            except InvalidOrMissingL402Header as e:
                try:
                    resp = Response(status=402)
                    price_in_usd_cents = get_price_func(request)
                    challenge = authenticator.new_challenge(price_in_usd_cents)
                    # Assuming new_challenge returns an object with a method ResponseHeader that formats the challenge string
                    resp.headers['WWW-Authenticate'] = challenge.response_header()
                    return resp
                except Exception:
                    return Response(status=500)
            except Exception:
                return Response(status=500)
        return decorated_function
    return decorator