from flask import Flask, request, make_response, jsonify
from l402.server import Authenticator, Flask_l402_decorator
from l402.server.invoice_provider import InvoiceProvider
from l402.server.macaroons import MacaroonService


class MockInvoiceProvider(InvoiceProvider):
    async def create_invoice(self, amount, currency, description):
        mock_invoice = "lnbcrt1u1p3d23dkpp58r92m0s0vyfdnd3caxhzgvu006dajv9r8pcspknhvezw26t9e8qsdq5g9kxy7fqd9h8vmmfvdjscqzpgxqyz5vqsp59efe44rg6cjl3xwh9glgx4ztcgwtg5l8uhry2v9v7s0zn2wpaz2s9qyyssq2z799an4pt4wtfy8yrk5ee0qqj7w5a74prz5tm8rulwez08ttlaz9xx7eqw7fe94y7t0600d03k55fyguyj24nd9tjmx6sf7dsxkk4gpkyenl8"
        mock_payment_hash = "38caadbe0f6112d9b638e9ae24338f7e9bd930a3387100da776644e56965c9c1"
        return mock_invoice, mock_payment_hash

class MockMacaroonService(MacaroonService):
    def __init__(self):
        self._store = {}

    async def insert_root_key(self, token_id, root_key, macaroon):
        self._store[token_id] = (root_key, macaroon)

    async def get_root_key(self, token_id):
        return self._store[token_id][0] if token_id in self._store else None
    
authenticator = Authenticator(
    location="https://example.com", 
    invoice_provider=MockInvoiceProvider(),
    macaroon_service=MockMacaroonService()
)

def pricing_func(request):
    return 1, "USD", "L402 protected endpoint"


app = Flask(__name__)

@app.route('/public')
def public_endpoint():
    return jsonify({"message": "pong"})

@app.route('/protected')
@Flask_l402_decorator(authenticator, pricing_func)
def protected_endpoint():
    return jsonify({"message": "Access granted to protected endpoint"})

if __name__ == '__main__':
    app.run()