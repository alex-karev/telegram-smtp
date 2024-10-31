#!.env/bin/python
from time import sleep
import json
from smtp import SMTP

with open("settings.json", "r") as f:
    settings = json.loads(f.read())

def smtp_callback(source, targets, subject, message):
    for target in targets:
        print("\n------\nFrom: {}\nTo: {}\nSubject: {}\n\n{}".format(source, target, subject, message))

def main():
    smtp = SMTP(**settings["smtp"], callback=smtp_callback)
    sleep(60*10)
    print("start")

if __name__ == "__main__":
    main()
