import os
from l402.client import requests
from l402.client.preimage_provider import AlbyAPI
from l402.client.credentials import SqliteCredentialsService

# Configure the client with AlbyAPI and SqliteCredentialsService
alby_token = os.getenv("ALBY_TOKEN")
if not alby_token:
    raise ValueError("ALBY_TOKEN environment variable is not set")

requests.configure(
    preimage_provider=AlbyAPI(api_key=alby_token),
    credentials_service=SqliteCredentialsService(":memory:")
)

# Example URL that requires L402 authentication
protected_url = "https://api.fewsats.com/v0/storage/download/2e54ac29-5945-4b5f-93db-998a535a5a49"

# Make a GET request to the protected resource
response = requests.get(protected_url)

# Check if the request was successful
response.raise_for_status()

# Get the file name and extension from the response headers
file_name = response.headers.get("File-Name", "downloaded_file")
file_extension = os.path.splitext(response.headers.get("Content-Disposition", ""))[1]

# Save the response content as a file
with open(f"{file_name}.{file_extension}", "wb") as f:
    f.write(response.content)


print(f"\nFile '{file_name}' downloaded successfully.")
