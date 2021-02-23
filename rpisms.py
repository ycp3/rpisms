import mailfunc
import directions
#import remindme
import time
import sys
from imapclient import IMAPClient

# time in seconds between inbox checks
interval = 30

HOST = "imap.gmail.com"
# gmail username + password
USERNAME = "USERNAME@gmail.com"
PASSWORD = "PASSWORD"

server = IMAPClient(HOST)
server.login(USERNAME, PASSWORD)
server.select_folder("INBOX")

server.idle()

while True:
    try:
        starttime = time.monotonic()
        responses = server.idle_check(timeout=interval)
        if responses:
            print(responses)
            if responses[0][1] == b'EXISTS':
                messages = mailfunc.check()
                print("CHECKING")
                for msg in messages:
                    if msg.lower().startswith("directions"):
                        if directions.validate(msg):
                            mailfunc.send(directions.get_directions(msg))
                        else:
                            mailfunc.send("Invalid input")
                    elif msg.lower().startswith("remind"):
                        pass # not implemented
                    else:
                        mailfunc.send("Unknown command")

                mailfunc.clearinbox()

        if time.monotonic() - starttime >= 13*60:
            server.idle_done()
            server.idle()
    
    except KeyboardInterrupt:
        break

server.idle_done()
server.logout()