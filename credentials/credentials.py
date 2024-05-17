import re

class L402Credentials:
    def __init__(self, macaroon, preimage, invoice):
        self.macaroon = macaroon
        self.preimage = preimage
        self.invoice = invoice

    def authentication_header(self):
       return f"L402 {self.macaroon}:{self.preimage}"

def parse_l402_challenge(response):
    challenge = response.headers.get('WWW-Authenticate')
    if not challenge:
        raise ValueError("WWW-Authenticate header missing.")
    
    return _parse_challenge(challenge)

def _parse_challenge(challenge):
    challenge = challenge.replace("\"", "")
    macaroon_match = re.search(r'macaroon=([^ ]+)', challenge)
    invoice_match = re.search(r'invoice=([^ ]+)', challenge)

    if not macaroon_match or not invoice_match:
        raise ValueError("Challenge parsing failed, macaroon or invoice missing.")

    macaroon = macaroon_match.group(1)
    invoice = invoice_match.group(1)
    # Assuming preimage is obtained after payment, which is not part of the challenge
    preimage = None

    return L402Credentials(macaroon, preimage, invoice)
