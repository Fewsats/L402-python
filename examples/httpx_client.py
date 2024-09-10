import os
from l402.client import requests
from l402.client.preimage_provider import AlbyAPI
from l402.client.credentials import SqliteCredentialsService

SERVER_URL = "https://api.fewsats.com"

alby_token = os.getenv("ALBY_TOKEN")
if not alby_token:
    raise ValueError("ALBY_TOKEN environment variable is not set")

requests.configure(
    preimage_provider=AlbyAPI(api_key=alby_token),
    credentials_service=SqliteCredentialsService()
)

external_id = '2e54ac29-5945-4b5f-93db-998a535a5a49'
response = requests.get(f"{SERVER_URL}/v0/storage/download/{external_id}")

response.raise_for_status()

file_name = response.headers.get("File-Name", "downloaded_file")

with open(f"{file_name}.jpg", "wb") as f:
    f.write(response.content)

print(f"\nFile '{file_name}' downloaded successfully.")