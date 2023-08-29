import hashlib
import json
import os.path
import urllib.parse

import pyotp
import pyperclip


def get_algorithms() -> dict:
    return {
        "SHA1": hashlib.sha1,
        "SHA256": hashlib.sha256,
        "SHA512": hashlib.sha512,
    }


def get_totp(otp_url: str) -> pyotp.TOTP | None:
    parsed_url = urllib.parse.urlparse(otp_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    algorithm = hashlib.sha1

    try:
        issuer = query_params['issuer'][0]
        secret_key = query_params['secret'][0]
    except KeyError:
        print("Error: issuer and secret must both be present")
        return None

    try:
        encryption = query_params.get('algorithm', ['SHA1'])[0]
        algorithms = get_algorithms()
        if encryption.upper() in algorithms:
            algorithm = algorithms[encryption.upper()]
    except KeyError:
        pass

    totp = pyotp.TOTP(secret_key, issuer=issuer, digest=algorithm)
    return totp


def main():
    parent_dir = os.path.dirname(__file__)
    credential_path = os.path.join(parent_dir, "credentials.json")

    with open(credential_path) as credential_json_file:
        data = json.load(credential_json_file)

        print("Please select which two-factor code to copy:")
        for i, otp_entry in enumerate(data["otpauth"], start=1):
            print(f'{i}) {otp_entry["name"]}')

        valid_input = False

        while not valid_input:
            try:
                selection = input("Selection: ")
                selection_int = int(selection)
                if 1 <= selection_int <= len(data["otpauth"]):
                    otp_entry = data["otpauth"][selection_int - 1]
                    totp = get_totp(otp_entry["url"])
                    pyperclip.copy(totp.now())
                    print(f'Copied {totp.now()} for {otp_entry["name"]}')
                    valid_input = True
                else:
                    print("Invalid input, please try again")
            except ValueError:
                print("Invalid input, please try again")


if __name__ == '__main__':
    main()
