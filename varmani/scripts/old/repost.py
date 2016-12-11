import json, time
from varmani.scripts.emailService import EmailService
from varmani.scripts.frappeclient import FrappeClient
import socket, select, string, sys
from varmani.scripts.messageService import MessageSerice

accessDetails = open('/home/hemant/access.txt')
aD = json.loads(accessDetails.read())

client = FrappeClient(aD['url'], aD['username'], aD['password'])
post = client.get_api("varmani.get_pi")
for pi in post:
    print(pi["name"])
    client.get_api("varmani.repost_pi","name="+pi["name"])
