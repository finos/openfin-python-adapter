import collections

class SubKey(collections.namedtuple("SubKey", ['uuid', 'name', 'topic'])):
    """
    Subscription key, which consists of a UUID, Name, and Topic
    """
    __slots__ = ()

    def __new__(cls, uuid=None, name=None, topic=None):
        if uuid is None:
            uuid = '*'
        if name is None:
            name = '*'
        if topic is None:
            topic = '*'
        return super(SubKey, cls).__new__(cls, uuid, name, topic)

    @classmethod
    def from_string(cls, topic):
        """
        Make a SubKey from a single string i.e: SubKey(topic=arg),
        or return the existing object if it is already a SubKey
        """
        if isinstance(topic, cls):
            return topic
        return cls(topic=topic)
