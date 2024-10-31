#!.env/bin/python
from smtplib import SMTP as Client
import json

def main():
    with open("settings.json", "r") as f:
        settings = json.loads(f.read())["smtp"]
        user = settings["users"][0]
    client = Client(settings["hostname"], settings["port"])
    client.ehlo()
    if settings["require_tls"]:
        client.starttls()
    if settings["require_auth"]:
        client.login(user["name"], user["password"])
    source = "info@{}".format(settings["domain"])
    targets = ["test@mail.com"]
    client.sendmail(source, targets, 
        """
        From: Anne Person {}
        To: Bart Person {}
        Subject: Test Message
        Message-ID: <ant>
        This is a test message!
        """.format(source, targets[0])
    )

if __name__ == "__main__":
    main()
