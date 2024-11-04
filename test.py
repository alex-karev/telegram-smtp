#!.env/bin/python
from smtplib import SMTP as Client
from email.mime.text import MIMEText
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
    msg = MIMEText(test_data["message"], "plain", 'utf-8')
    msg['Subject'] = test_data["subject"]
    msg['From'] = source
    msg['To'] = test_data["target"]
    client.sendmail(source, test_data["target"], msg.as_string())

if __name__ == "__main__":
    main()
