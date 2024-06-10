# L402 Python Library

The L402 Python Library provides a client and server implementation of the L402 protocol for handling HTTP 402 Payment Required responses. It allows you to easily integrate payments into your Python applications.

## Features

- Client-side handling of HTTP 402 Payment Required responses
- Server-side authentication and invoice generation for protected resources
- Pluggable interfaces for invoice providers and credential storage
- Built on top of popular libraries like httpx and Flask

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

#Configure the client with a preimage provider and credentials service
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

@app.route('/protected')
@Flask_l402_decorator(authenticator, pricing_func)
def protected_route():
    return "Protected content"
```


## Contributing

Contributions are welcome! Please see the contributing guide for more information.
