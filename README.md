# local-two-factor-tool
This can't be safe.

-------
### What it does
Completely ruin the point of having 2 factor auth. Anyway, a picture is worth a thousand words:
![2023-08-28_16-45](https://github.com/xantaren/local-two-factor-tool/assets/68090976/82a2a493-7a4b-447c-87e5-06bc1bebec89)

### How to use
1. Change or append to the array under `otpauth` of credential.json.
    1. `name` can be anything you want
    2. `url` is what you get when you scan the QR Code for setting up 2 factor.
2. Run `main.py` with Python3
