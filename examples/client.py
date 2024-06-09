from l402.client import requests, PreimageProvider, CredentialsService

SERVER_URL = "http://127.0.0.1:5000"

class MockPreimageProvider(PreimageProvider):
    async def get_preimage(self, invoice):
        print(invoice)
        # Preimage for "lnbcrt1u1p3d23dkpp58r92m0s0vyfdnd3caxhzgvu006dajv9r8pcspknhvezw26t9e8qsdq5g9kxy7fqd9h8vmmfvdjscqzpgxqyz5vqsp59efe44rg6cjl3xwh9glgx4ztcgwtg5l8uhry2v9v7s0zn2wpaz2s9qyyssq2z799an4pt4wtfy8yrk5ee0qqj7w5a74prz5tm8rulwez08ttlaz9xx7eqw7fe94y7t0600d03k55fyguyj24nd9tjmx6sf7dsxkk4gpkyenl8"
        return "2f84e22556af9919f695d7761f404e98ff98058b7d32074de8c0c83bf63eecd7"

class MockCredentialsService(CredentialsService):
    def __init__(self):
        self._credentials = {}
    async def store(self, credentials):
        self._credentials[credentials.location] = credentials

    async def get(self, location):
        return self._credentials.get(location, None)
    
  
requests.configure(
    preimage_provider=MockPreimageProvider(),
    credentials_service=MockCredentialsService()
)

print(requests.get("http://127.0.0.1:5000/public"))
print(requests.get("http://127.0.0.1:5000/protected"))