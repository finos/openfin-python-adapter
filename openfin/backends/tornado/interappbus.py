from tornado import gen
from ...utils.logger import logger


class InterApplicationBusPrivateMixin(object):
    """
    Mixin class providing the private methods corresponding to fin.InterApplicationBus

    Don't use this class directly, it should only be mixed into the private OpenFinTornadoWebSocket
    """

    @gen.coroutine
    def subscribe(self, key):
        """
        Subscribe to the interapp bus
        """

        logger.debug(
            "Adding subscription to uuid: {uuid}, name: {name}, topic: {topic}".format(
                **key._asdict()))
        _ = yield self._action('subscribe', {
            'sourceUuid': key.uuid,
            'sourceWindowName': key.name,
            'topic': key.topic,
            'destinationWindowName': self.uuid})

    @gen.coroutine
    def unsubscribe(self, key):
        """
        Unsubscribe from the interapp bus
        """

        logger.debug(
            "Removing subscription to uuid: {uuid}, name: {name}, topic: {topic}".format(
                **key._asdict()))
        _ = yield self._action('unsubscribe', {
            'sourceUuid': key.uuid,
            'sourceWindowName': key.name,
            'topic': key.topic,
            'destinationWindowName': self.uuid})

    @gen.coroutine
    def publish_message(self, topic, message):
        """
        Publish a message to the interapp bus
        """

        _ = yield self._action('publish-message', {
            'topic': topic,
            'message': message,
            'sourceWindowName': self.uuid,
        })

    @gen.coroutine
    def send_message(self, key, message):
        """
        Send a message to a specific destination on the interapp bus
        """

        _ = yield self._action('send-message', {
            'destinationUuid': key.uuid,
            'destinationWindowName': key.name,
            'topic': key.topic,
            'message': message,
            'sourceWindowName': self.uuid,
        })
