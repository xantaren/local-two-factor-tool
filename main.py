import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
import json
import os.path
import urllib.parse
import pyotp
import pyperclip

PARAM_SECRET = "secret"
PARAM_ISSUER = "issuer"
PARAM_ALGORITHM = "algorithm"


class OtpData:
    def __init__(self, otp_url):
        self._otp_url = otp_url
        self._title = ""
        self._name = ""
        self._organization = ""
        self._secret = ""
        self._issuer = ""
        self._algorithm = ""

        self._parse_otp_url()

    def get_title(self) -> str:
        return self._title

    def set_title(self, title) -> any:
        self._title = title
        return self

    def get_name(self) -> str:
        return self._name

    def get_organization(self) -> str:
        return self._organization

    def get_secret(self) -> str:
        return self._secret

    def get_issuer(self) -> str:
        return self._issuer

    def get_algorithm(self) -> str:
        return self._algorithm

    def _parse_otp_url(self):
        parsed_url = urllib.parse.urlparse(self._otp_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if PARAM_SECRET not in query_params.keys():
            raise Exception(f"Missing {PARAM_SECRET} parameter in otp URL")

        if PARAM_ISSUER not in query_params.keys():
            raise Exception(f"Missing {PARAM_ISSUER} parameter in otp URL")

        url_components = parsed_url.path.split(":")
        title = url_components[0][1:]

        self._title = title
        self._secret = query_params.get(PARAM_SECRET)[0]
        self._issuer = query_params.get(PARAM_ISSUER)[0]
        self._algorithm = query_params.get(PARAM_ALGORITHM, [""])[0]


class Model:
    def __init__(self, data_source: str):
        self.data_source = data_source

    def _get_credentials_json(self) -> str:
        if not os.path.exists(self.data_source):
            return ""

        with open(self.data_source) as credential_json_file:
            return json.load(credential_json_file)

    def get_all_otp_data(self) -> [OtpData]:
        if not os.path.exists(self.data_source):
            return []

        with open(self.data_source) as credential_json_file:
            data = json.load(credential_json_file)

        all_otp_data = []
        for info in data["otpauth"]:
            all_otp_data.append(OtpData(info["url"]).set_title(info["name"]))
        return all_otp_data


class View:
    def __init__(self):
        self.root = tk.Tk()
        self.__configure_root_style()

    def __configure_root_style(self):
        style = ttk.Style(self.root)
        style.configure("TButton", font=("Helvetica", 12))

    def set_title(self, title: str):
        self.root.title(title)
        return self

    def set_dimensions(self, dimension_literals: str):
        self.root.geometry(dimension_literals)
        return self

    def get_root(self):
        return self.root

    def display(self):
        self.root.mainloop()


class Controller:
    def __init__(self):
        pass


def get_algorithms() -> dict:
    return {
        "SHA1": hashlib.sha1,
        "SHA256": hashlib.sha256,
        "SHA512": hashlib.sha512,
    }


def copy_totp_top_clipboard(selected_entry: OtpData):
    algorithm = hashlib.sha1

    try:
        encryption = selected_entry.get_algorithm()
        if encryption == "":
            encryption = "SHA1"
        algorithms = get_algorithms()
        if encryption.upper() in algorithms:
            algorithm = algorithms[encryption.upper()]
    except KeyError:
        pass

    totp = pyotp.TOTP(selected_entry.get_secret(), issuer=selected_entry.get_issuer(), digest=algorithm)

    if totp:
        pyperclip.copy(totp.now())
        messagebox.showinfo("Copy Complete", f'Copied {totp.now()} for {selected_entry.get_title()} to clipboard')


def on_select(data: [OtpData], listbox):
    selection = listbox.curselection()
    if selection:
        selected_index = selection[0]
        selected_entry = data[selected_index]
        copy_totp_top_clipboard(selected_entry)


def main():
    parent_dir = os.path.dirname(__file__)
    credential_path = os.path.join(parent_dir, "credentials.json")

    model = Model(credential_path)
    otp_data = model.get_all_otp_data()

    view = View()
    root = view.set_title("OTP Manager").set_dimensions("400x350").get_root()

    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

    label = tk.Label(frame, text="Please select which two-factor code to copy:")
    label.pack(pady=10, anchor="w")

    listbox = tk.Listbox(frame, selectmode=tk.SINGLE, font=("Helvetica", 12))
    listbox.pack(fill=tk.BOTH, expand=True)
    listbox.bind("<Double-1>", lambda event: on_select(otp_data, listbox))

    scrollbar = tk.Scrollbar(listbox, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

    listbox.config(yscrollcommand=scrollbar.set)

    for i, data in enumerate(otp_data):
        listbox.insert(i, data.get_title())

    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)

    exit_button = ttk.Button(button_frame, text="Exit", command=root.destroy)
    exit_button.pack(side=tk.LEFT, padx=10)

    copy_button = ttk.Button(button_frame, text="Copy", command=lambda: on_select(otp_data, listbox))
    copy_button.pack(side=tk.LEFT, padx=10)

    root.mainloop()


if __name__ == '__main__':
    main()
