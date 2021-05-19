from .key import SubKey
from .system import SystemAPIMixin
from ..exceptions import OpenFinWebSocketException
from ..utils.constants import (WS_INIT, WS_OPEN, WS_CLOSED)
from ..backends.tornado.ws import OpenFinTornadoWebSocket
import sys
if sys.platform == 'win32':
    import win32file
import struct 
import os


OPENFIN_RVM_EXECUTABLE = os.environ.get('OPENFIN_RVM_EXECUTABLE', os.path.join(os.environ.get('LOCALAPPDATA', ''), 'OpenFin', 'OpenFinRVM.exe'))

RUNTIME_HELLO_MESSAGE = 2**16 - 1
RUNTIME_STRING_MESSAGE = 0


class OpenFinClient(SystemAPIMixin):
    """
    Public interface to connect to OpenFin
    """

    def __init__( self, backend=OpenFinTornadoWebSocket ):
        self._backend_class = backend
        port = self._get_port()        
        self.url = 'ws://localhost:'+str(port)+'/'        
        self.connect()

    def _read_from_pipe( self, named_pipe, read_buffer ):
        # Header
        result, header = win32file.ReadFile(named_pipe, read_buffer, None)
        struct_obj = struct.Struct( 'IIIII' )
        payload_size, routing_id, message_type, flags, attachment_count = struct_obj.unpack( header )

        if message_type == RUNTIME_HELLO_MESSAGE:
            # Hello message
            result, data = win32file.ReadFile(named_pipe, payload_size, None)
            struct_obj2 = struct.Struct( 'I'*int(payload_size/4) )
            msg = struct_obj2.unpack( data )
            return msg, (payload_size, routing_id, message_type, flags, attachment_count)

        elif message_type == RUNTIME_STRING_MESSAGE:  
            # Literal string message
            result, data = win32file.ReadFile(named_pipe, payload_size, None)
            return data[4:data.rfind('}'.encode())+1], None

    def _launch_RVM( self ):
        ''' Start the RVM '''
        import json, os
        from subprocess import call

        # Create and write the config file
        config_json = {
            "runtime": {
                "version": "9.61.32.38"
            },
        }        
        with open('my_config.json', 'w') as outfile:  
            json.dump(config_json, outfile)                    
        filename = os.path.join( os.getcwd(), 'my_config.json' )

        # Define the command and run it
        runtimeArgs = "--runtime-arguments=--runtime-information-channel-v6=" + self._pipe_name        
        cmd = [
            '{}'.format(OPENFIN_RVM_EXECUTABLE),
            '--launch',
            '--config={}'.format(filename),
            runtimeArgs,
            ]        
        call( cmd )        

    def _get_port( self ):
        if sys.platform == 'win32':
            import win32pipe
            import os
            import json                       

            # Choose a pipe name
            self._pipe_name = 'PythonAdapter.{}'.format( os.getpid() )
            
            # Create a read buffer
            read_buffer = win32file.AllocateReadBuffer(20)

            # Create the named pipe
            named_pipe = win32pipe.CreateNamedPipe( r'\\.\pipe\chrome.{}'.format( self._pipe_name ),
                                            win32pipe.PIPE_ACCESS_DUPLEX,
                                            0,
                                            1,
                                            65536,
                                            65536,
                                            300,
                                            None)        

            # Start the RVM - NO , this will be started from an external process
            self._launch_RVM()

            # Connect the pipe
            win32pipe.ConnectNamedPipe(named_pipe)    

            # Read from the pipe, first time, should be a hello message
            msg, headers = self._read_from_pipe( named_pipe, read_buffer )
            
            # Write hello message to the pipe
            # https://github.com/HadoukenIO/js-adapter/blob/develop/src/transport/port-discovery.ts#L157 
            write_buffer = win32file.AllocateReadBuffer(24)
            hello_struct0 = struct.Struct('IIIII')
            hello_struct0.pack_into( write_buffer, 0, *(headers) )
            hello_struct1 = struct.Struct('I')
            hello_struct1.pack_into( write_buffer, 20, *msg )
            win32file.WriteFile(named_pipe, write_buffer, None) # Send the PID
            
            # Read from the pipe, second time, should be a string message
            msg, headers = self._read_from_pipe( named_pipe, read_buffer )  
            message = json.loads(msg)
            payload = message.get('payload')
            if payload:
                return payload.get('port')
        return 9696

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
