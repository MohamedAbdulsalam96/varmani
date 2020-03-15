import json
from scripts.frappeclient import FrappeClient

accessDetails = open('/home/hemant/access.txt')
aD = json.loads(accessDetails.read())

client = FrappeClient(aD['url'], aD['username'], aD['password'])
post = client.get_api("varmani.get_pi")
for pi in post:
    print(pi["name"])
    client.get_api("varmani.repost_pi","name="+pi["name"])
