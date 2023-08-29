# local-two-factor-tool
This can't be safe.

-------
### What it does
Completely ruin the point of having 2 factor auth. Anyway, a picture is worth a thousand words:
![2023-08-29_09-14](https://github.com/xantaren/local-two-factor-tool/assets/68090976/9c804fb6-00f4-4dde-bf9d-d5c7a6eb3a14)

### How to use
1. Make a copy of `credentials_example.json` and rename it to `credentials.json`
2. Change or append to the array under `otpauth` of `credentials.json`.
    1. `name` can be anything you want
    2. `url` is what you get when you scan the QR Code for setting up 2 factor.
3. Run `main.py` with Python3
