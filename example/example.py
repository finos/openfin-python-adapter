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

for index in range(0, 10):
    client.publish("example", json.loads('{"test":' + str(index) + '}'))
    time.sleep(random.random())

text = input()
