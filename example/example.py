import openfin
import time
import random
import json

client = openfin.OpenFinClient()


def log_message(*args, **kwargs):
    print(args, kwargs)


def on_register(val):
    print("Registered")


client.subscribe(openfin.SubKey.from_string("example"), log_message, on_register)

payload = {
  "title": "Salesforce to Purchase Slack for $28Bil",
  "body": "The two companies have entered into a definitive agreement for sale in cash and stock...\n        ![](https://cdn.openfin.co/examples/notifications/graph1.png)",
  "icon": "https://cdn.openfin.co/examples/notifications/factset.png",
  "category": "news",
  "buttons": [
    {
      "title": "Read More",
      "cta": "true"
    }
  ],
  "catalogId": "c12475ba-9d1b-4ac6-a45f-0e2121902674"
}

for index in range(0, 10):
    #client.publish("example", '{ test:' + str(index) + '}')
    client.publish("example", json.dumps('{'+ str(index) +':' +  str(payload) +'}'))
    time.sleep(random.random())

text = input()
