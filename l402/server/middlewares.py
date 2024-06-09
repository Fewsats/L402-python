from typing import Callable, Tuple, Coroutine, Any
import asyncio

from fastapi import Request, HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware
from functools import wraps
from flask import request, make_response, current_app

from l402.server import Authenticator

class FastAPIL402Middleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app,
        authenticator: Authenticator, 
        pricing_func: Callable[[Request], Tuple[str, str, str]],
    ):
        super().__init__(app)
        self.authenticator = authenticator
        self.pricing_func = pricing_func

    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable[[Request], Coroutine[Any, Any, Response]],
    ) -> Response:

        header = request.headers.get("Authorization")
        if header:
            try:
                await self.authenticator.validate_l402_header(header)
                return await call_next(request)
            except Exception as e:
                pass
        
        amount, currency, description = self.pricing_func(request)
        macaroon, payment_request = await self.authenticator.new_challenge(amount, currency, description)
        response = HTTPException(status_code=402, detail="Payment Required")
        response.headers["WWW-Authenticate"] = f'L402 macaroon="{macaroon}", invoice="{payment_request}"'
        raise response


def Flask_l402_decorator(authenticator, pricing_func):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            async def async_wrapper():
                with current_app.app_context():
                    header = request.headers.get("Authorization")
                    if header:
                        try:
                            await authenticator.validate_l402_header(header)
                            if asyncio.iscoroutinefunction(func):
                                response = await func(*args, **kwargs)
                            else:
                                response = func(*args, **kwargs)
                            return response
                        
                        except Exception as e:
                            pass

                    amount, currency, description = pricing_func(request)
                    macaroon, payment_request = await authenticator.new_challenge(amount, currency, description)
                    response = make_response("Payment Required", 402)
                    response.headers["WWW-Authenticate"] = f'L402 macaroon="{macaroon}", invoice="{payment_request}"'
                    return response

            return asyncio.run(async_wrapper())

        return wrapper

    return decorator