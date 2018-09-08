import openfin
import time
import random

client = openfin.OpenFinClient()

def log_message( *args, **kwargs ):
    print args, kwargs

client.subscribe(openfin.SubKey.from_string("example"), log_message)

for index in xrange(0, 10):
    client.publish("example", "I am message " + str( index ) + " from python.")
    time.sleep(random.random())