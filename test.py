#!.env/bin/python
from smtplib import SMTP as Client
import json

def main():
    with open("settings.json", "r") as f:
        settings = json.loads(f.read())
        test_data = settings["test"]
        settings = settings["smtp"]
        user = settings["users"][0]
    client = Client(settings["hostname"], settings["port"])
    client.ehlo()
    if settings["require_tls"]:
        client.starttls()
    if settings["require_auth"]:
        client.login(user["name"], user["password"])
    source = "info@{}".format(settings["domain"])
    client.sendmail(source, test_data["target"], 
        """
        From: Anne Person {}
        To: Bart Person {}
        Subject: Test Message
        Message-ID: <ant>
        {}
        """.format(source, test_data["target"], test_data["message"])
    )

if __name__ == "__main__":
    main()
