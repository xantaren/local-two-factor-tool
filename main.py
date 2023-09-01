import tkinter as tk
from tkinter import messagebox, ttk
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


def get_totp(otp_url: str) -> any:
    parsed_url = urllib.parse.urlparse(otp_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    algorithm = hashlib.sha1

    try:
        issuer = query_params['issuer'][0]
        secret_key = query_params['secret'][0]
    except KeyError:
        messagebox.showerror("Error", "corrupt data, issuer and secret must both be present")
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


def copy_totp_top_clipboard(selected_entry):
    totp = get_totp(selected_entry["url"])
    if totp:
        pyperclip.copy(totp.now())
        messagebox.showinfo("Copy Complete", f'Copied {totp.now()} for {selected_entry["name"]} to clipboard')


def on_select(data, listbox):
    selection = listbox.curselection()
    if selection:
        selected_index = selection[0]
        selected_entry = data["otpauth"][int(selected_index)]
        copy_totp_top_clipboard(selected_entry)


def main():
    parent_dir = os.path.dirname(__file__)
    credential_path = os.path.join(parent_dir, "credentials.json")

    with open(credential_path) as credential_json_file:
        data = json.load(credential_json_file)

    root = tk.Tk()
    root.title("OTP Manager")
    root.geometry("400x350")  # Set the initial window size

    # Create a custom style for buttons
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12))

    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    label = tk.Label(frame, text="Please select which two-factor code to copy:")
    label.pack(pady=10)

    listbox = tk.Listbox(frame, selectmode=tk.SINGLE, font=("Helvetica", 12))
    listbox.pack(fill=tk.BOTH, expand=True)
    listbox.bind("<Double-1>", lambda event: on_select(data, listbox))

    scrollbar = tk.Scrollbar(listbox, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

    listbox.config(yscrollcommand=scrollbar.set)

    for i, otp_entry in enumerate(data["otpauth"]):
        listbox.insert(i, otp_entry["name"])

    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)

    exit_button = ttk.Button(button_frame, text="Exit", command=root.destroy)
    exit_button.pack(side=tk.LEFT, padx=10)

    copy_button = ttk.Button(button_frame, text="Copy", command=lambda: on_select(data, listbox))
    copy_button.pack(side=tk.LEFT, padx=10)

    root.mainloop()


if __name__ == '__main__':
    main()
