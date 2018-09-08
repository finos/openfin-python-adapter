from .key import SubKey
from .system import SystemAPIMixin
from ..exceptions import OpenFinWebSocketException
from ..utils.constants import (WS_INIT, WS_OPEN, WS_CLOSED)
from ..backends.tornado.ws import OpenFinTornadoWebSocket


class OpenFinClient(SystemAPIMixin):
    """
    Public interface to connect to OpenFin
    """

    def __init__(self, backend=OpenFinTornadoWebSocket):

        self._backend_class = backend

        # TODO: Does the message bus always bind to port 9696?
        self.url = 'ws://localhost:9696/'
        self.connect()

    def connect(self):
        """
        Connect to OpenFin

        This is called automatically in __init__, but can also be called manually
        to reconnect (say if the OpenFin Bus restarted). Re-connecting will not
        automatically restore any previous subscriptions.
        """
        self._ws = self._backend_class(self.url)

    def close(self):
        """
        Close the connection, ending all subscriptions
        """
        self._ws('close', callback=None)
        self._ws = None

    def status(self):
        """
        Return the status of the websocket (WS_INIT|WS_OPEN|WS_CLOSED)
        """

        if self._ws and self._ws.status:
            return self._ws.status
        return WS_CLOSED

    def _check_status(self):

        if self.status() == WS_CLOSED:
            raise OpenFinWebSocketException('WS is closed')

    @property
    def uuid(self):
        """ This client's UUID """
        return self._ws.uuid

    def publish(self, topic, message):
        """
        Publish a message to all subscribers for a given topic

        topic: either a string or a SubKey
        message: a json-serializable object
        """

        self._check_status()
        topic = SubKey.from_string(topic).topic
        self._ws('publish_message',
                 args=(topic, message),
                 callback=None)

    def send(self, destination, message):
        """
        Send a message to a specific subscriber

        destination: either SubKey or a string, which is equivalent to passing SubKey(topic=string)
        message: a json-serializable object
        """
        self._check_status()
        key = SubKey.from_string(destination)
        self._ws('send_message',
                 args=(key, message),
                 callback=None)

    def subscribe(self, source, on_message=None, on_register=None):
        """
        Subscribe to the InterApplication Bus, running the on_message callback
        whenever a message is sent to the given source

        Supports wildcard subscription:
        client.subscribe('*', callback=broadcast)

        source: either a SubKey or a string, which is equivalent to passing SubKey(topic=string)
        on_message: a callback to run on each message
        on_register: a callback that will run after the subscribe operation (useful for unit tests)
        """

        self._check_status()
        key = SubKey.from_string(source)
        self._ws.subscriptions.append((key, on_message))
        self._ws('subscribe', args=(key,), callback=on_register)

    def unsubscribe(self, source, on_message=None, on_register=None):
        """
        Unsubscribe from the InterApplication Bus

        source: either a SubKey or a string, which is equivalent to passing SubKey(topic=string)
        on_message: the callback function to remove. None will remove all subscriptions for this source
        on_register: a callback that will run after the unsubscribe operation (useful for unit tests)
        """

        target_key = SubKey.from_string(source)
        for ii, (active_key, callback) in enumerate(self._ws.subscriptions):
            if active_key == target_key and (
                    on_message is None or callback.id == on_message.id):
                del self._ws.subscriptions[ii]
        active_subscription_count = sum(
            active_key == target_key for (
                active_key, _) in self._ws.subscriptions)
        if active_subscription_count == 0:
            self._ws('unsubscribe', args=(target_key,), callback=on_register)
        else:
            on_register(None)
