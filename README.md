# L402 Python Library

This library simplifies the integration of internet-native paywalls into your Python applications by providing a client and server implementation of the L402 protocol.

HTTP servers like Flask and FastAPI can easily authorize and charge for requests, while clients can automatically gain access to protected services by obtaining credentials and paying invoices.

For learning more about the protocol, visit [l402.org]

## Features

- Built on top of the `HTTP 402 Payment Required` error code
- Fine-grained authorization policies using Macaroons, giving you granular control over service access
- Secure, fast, and cheap payments powered by the Lightning Network
- Allows payments as small as a fraction of a cent
- Machine-friendly design, perfect for seamless integration with AI-driven applications
- Async-first architecture for optimal performance
- Includes decorators and middlewares for popular HTTP servers: Flask, FastAPI, and Django
- Drop-in replacement for the `httpx` client, making it easy to access protected services

## Installation

The package is available at [pypi](https://pypi.org/project/l402/) and be installed with pip.

```bash
pip install l402
```

## Usage

### Client

To make requests that can handle 402 Payment Required responses:

```python
from l402.client import httpx

# Configure the client with a preimage provider and credentials service.
httpx.configure(
    preimage_provider=MyPreimageProvider(),
    credentials_service=MyCredentialsService()
)

# Make a request
async with httpx.AsyncClient() as client:
    response = await client.get("https://example.com/protected")
```

### Server

To protect routes and require payment:

```python
from flask import Flask
from l402.server import Authenticator, Flask_l402_decorator

app = Flask(name)
authenticator = Authenticator(...)

# Paywall a route with a 1 USD cent payment required.
def pricing_func(amount: int, currency: str, description: str):
    price_in_cents = 1
    return price_in_cents, "USD", "L402 challenge"

@app.route('/protected')
@Flask_l402_decorator(authenticator, pricing_func)
def protected_route():
    return "Protected content"
```

## Tutorial

If you want to learn more about the L402 protocol, how to set it up in your own server, or how to use the client library, we have a notebook tutorial to help you get started:
* [Colab](https://colab.research.google.com/drive/1MLZy1g6-lFqbRAfFOxR14PZ3b36sYr1r?usp=sharing)
* [Jupyter Notebook](https://github.com/Fewsats/L402-python/blob/main/examples/l402-tutorial.ipynb) 
* [Local](examples/l402-tutorial.ipynb)

We'll guide you through the process step by step, providing code examples and explanations along the way. By the end of this tutorial, you'll have a solid understanding of how to integrate internet-native paywalls into your Python applications using the L402 Python Library

## Contributing

Contributions are welcome! Please see the contributing guide for more information.
