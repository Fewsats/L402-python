class MemoryStore:
    def __init__(self):
        self.credentials_store = {}

    def get_l402_credentials(self, url, method):
        return self.credentials_store.get((url, method))

    def save_l402_credentials(self, url, method, credentials):
        self.credentials_store[(url, method)] = credentials
