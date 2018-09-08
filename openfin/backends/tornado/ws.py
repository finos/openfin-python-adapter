import threading
import uuid

import tornado.websocket
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.queues import Queue

try:
    import ujson as json
except BaseException:
    import json

from .interappbus import InterApplicationBusPrivateMixin
from .system import SystemPrivateMixin
from ...utils.constants import WS_INIT, WS_OPEN, WS_CLOSED
from ...utils.logger import logger

IO_LOOP_RUNNING = False


# TODO:
# Periodically ping the websocket server and raise an exception if it doesn't respond
# See ping_interval:
# http://www.tornadoweb.org/en/stable/websocket.html#client-side-support


class OpenFinTornadoWebSocket(InterApplicationBusPrivateMixin,
                              SystemPrivateMixin):
    """
    Private interface, this should only be accessed from OpenFinClient

    This should be the only class that interacts with tornado's io_loop
    or uses tornado features like @gen.coroutine. The public interface
    should completely hide the websocket backend from the user.

    All public methods on this class should be decorated with @gen.coroutine
    """

    def __init__(self, url):
        self.url = url

        self._start_io_loop()
        self._ws = tornado.websocket.websocket_connect(
            self.url, io_loop=self.io_loop)
        self.uuid = str(uuid.uuid4())
        self.message_id = 0
        self.subscriptions = []
        self.connection_messages = Queue()
        self.subscription_messages = Queue()
        self.ack_messages = Queue()
        self.status = WS_INIT

        self.io_loop.add_callback(self._connect)
        self.io_loop.add_callback(self._read_loop)
        self.io_loop.add_callback(self._subscription_loop)

    def __call__(self, method_name, args=None, kwargs=None, callback=None):
        """
        Run a future and then run the callback once it completes

        This is the primary entry point the public interface should call to send
        messages to the websocket. All of the public methods on this class should
        be accessed via the __call__ method.
        """

        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = {}

        # If there's specific logic for this endpoint, use it,
        # otherwise create a default handler
        if hasattr(self, method_name):
            method = getattr(self, method_name)
        else:

            @gen.coroutine
            def method(*args, **kwargs):
                payload = yield self._action(method_name)
                result = payload.get('data') if payload else None
                raise gen.Return(result)

        def wrapped():
            future = method(*args, **kwargs)
            if callback:
                future.add_done_callback(lambda ff: callback(ff.result()))

        self.io_loop.add_callback(wrapped)

    def _start_io_loop(self):
        """
        Start a tornado IOLoop (if one is not already running)
        """
        global IO_LOOP_RUNNING
        self.io_loop = IOLoop().current()
        if not IO_LOOP_RUNNING:
            logger.debug('Starting Tornado IOLoop in thread')
            IO_LOOP_RUNNING = True
            thread = threading.Thread(target=self.io_loop.start)
            thread.daemon = True
            thread.start()

    @gen.coroutine
    def _connect(self):
        """
        Run the OpenFin connection handshake
        """
        msg = {
            'action': 'request-external-authorization',
            'payload': {
                'uuid': self.uuid,
                'type': 'file-token',
                'messageId': self.message_id,
            }
        }

        try:
            ws = yield self._ws
        except BaseException:
            logger.exception('Could not connect to Openfin bus')
            self.close()
            raise gen.Return()

        ws.write_message(json.dumps(msg))
        response1 = yield self.connection_messages.get()

        filename = response1['payload']['file']
        token = response1['payload']['token']

        with open(filename, 'w') as fp:
            fp.write(token)

        msg2 = {
            'action': 'request-authorization',
            'payload': {
                'address': self.url,
                'uuid': self.uuid,
                'type': 'file-token',
            }
        }

        ws.write_message(json.dumps(msg2))
        response2 = yield self.connection_messages.get()

        if (response2['action'] == 'authorization-response' and response2['payload']['success']):
            self.status = WS_OPEN
        else:
            self.close()
            logger.error("Openfin connection failed: {}".format(
                response2['payload']['reason']))

    @gen.coroutine
    def _wait_for_connection(self):
        """
        Queue other requests until the handshake is complete

        The openfin message bus will drop some requests (such as subscribe)
        if they are sent before the connection handshake is complete
        """
        tries = 0
        while self.status == WS_INIT:
            if tries > 2:
                logger.debug('Waiting for connection...')
            tries += 1
            sleep_time = 2**tries * .5
            yield gen.sleep(sleep_time)

    @gen.coroutine
    def _read_loop(self):
        """
        Read raw messages off the websocket and place them in queues for consumption

        This should be the only method that calls "ws.read_message()"
        """
        try:
            ws = yield self._ws
        except BaseException:
            logger.error('Websocket is closed')
            self.close()
        while self.status != WS_CLOSED:
            try:
                msg = yield ws.read_message()

                # A message of None means the other side closed the connection
                if msg is None:
                    self.close()
                    break

            except Exception:
                logger.exception(
                    "Caught error attempting to read from websocket, closing..."
                )
                self.close()
                break

            try:
                parsed = json.loads(msg)
            except BaseException:
                logger.exception(
                    "Could not parse JSON message: {}".format(msg))
            else:
                if parsed['action'] == 'ack':
                    self.ack_messages.put(parsed)
                elif parsed['action'] == 'process-message':
                    self.subscription_messages.put(parsed)
                elif (parsed['action'] == 'external-authorization-response'
                      or parsed['action'] == 'authorization-response'):
                    self.connection_messages.put(parsed)
                elif parsed['action'] in ('subscriber-added',
                                          'subscriber-removed'):
                    # TODO: Do we need to do anything with this?
                    # {"action":"subscriber-added","payload":{"senderName":"*","senderUuid":"*","targetName":"bqpp372toy14hpsjye6wasjor","topic":"*","uuid":"bqpp372toy14hpsjye6wasjor"}}
                    pass
                else:
                    logger.warn(
                        "Unknown message type, dropping message: {}".format(
                            msg))

    @gen.coroutine
    def _subscription_loop(self):
        """
        Dispatch subscription messages
        """

        while self.status != WS_CLOSED:
            message = yield self.subscription_messages.get()
            self._handle_subscriptions(message)

    def _handle_subscriptions(self, message):
        """
        Dispatch subscription messages
        """

        source_app = message['payload'].get('sourceUuid', '*')
        target_uuid = message['payload'].get('destinationUuid', '*')
        target_name = message['payload'].get('destinationWindowName', '*')
        target_topic = message['payload'].get('topic', '*')

        # Ignore messages from self
        if source_app == self.uuid:
            return

        for key, callback in self.subscriptions:
            if all((key_elem == '*') or (key_elem == target_elem)
                   for (key_elem,
                        target_elem) in zip(key, (target_uuid, target_name,
                                                  target_topic))):
                callback(message['payload']['message'])

    @gen.coroutine
    def _action(self, action, payload=None):
        """
        Send an OpenFin request
        """

        # Subscription requests are only accepted by the bus after the connection handshake
        # Some other requests (such as get-version) seem to work before the handshake,
        # but I'm not sure if that's intentional.
        # This requires everything to have an active connection
        yield self._wait_for_connection()

        if self.status != WS_OPEN:
            logger.error(
                'Websocket is closed, cannot send request: {}'.format(action))
            raise gen.Return(None)

        if payload is None:
            payload = {}

        request_id = self.message_id
        msg = {
            'action': action,
            'payload': payload,
            'messageId': request_id,
        }
        self.message_id += 1

        ws = yield self._ws
        ws.write_message(json.dumps(msg))
        try:
            response = yield self.ack_messages.get()
        except Exception as err:
            logger.warn("Caught exception in _action: {}".format(err))
            raise gen.Return()

        # Drop the response if it doesn't match what the user was expecting
        response_id = response['correlationId']
        if request_id != response_id:
            logger.warn(
                'Request ID is {}, but response ID is {}. Dropping message'.
                format(request_id, response_id, response))
            raise gen.Return()

        raise gen.Return(response['payload'])

    @gen.coroutine
    def close(self):
        """
        Close the websocket
        """

        if not self.status == WS_CLOSED:
            self.status = WS_CLOSED

            try:
                ws = yield self._ws
                # Code and reason are mandatory, not optional as the docs claim
                # :)
                ws.close(code=1000, reason='Closing websocket')
            except BaseException:
                # The websocket is already closed
                pass
