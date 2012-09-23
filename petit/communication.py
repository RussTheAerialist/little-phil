import zmq

import petit.lib as lib

def factory(config):
    return _Factory(config)

class _Factory(lib._BaseObject):
    _context = None
    _DEFAULT_HOSTS = {
        'ipc': '/tmp/petit',
        'inproc': 'petit',
    }

    _SEP = {
        'ipc': '/',
        'inproc': '#',
    }

    _INIT = {
        zmq.SUB: lambda x, args: x.setsockopt(zmq.SUBSCRIBE, args[0]),
    }

    _CONNECT = {
        True: lambda x,sock: x.bind(sock),
        False: lambda x,sock: x.connect(sock)
    }

    def __init__(self, config):
        super(_Factory, self).__init__(config)

        # We should only have a single ZMQ context per process.
        if _Factory._context is None:
            _Factory._context = zmq.Context()
        self._protocol = self._config['network'].get('protocol', 'ipc')
        self._sep = self._SEP.get(self._protocol, ':')

    def _create_connection(self, socket_type, port, bind, host=None, *args):
        protocol = self._protocol
        if host is None:
            host = self._DEFAULT_HOSTS.get(protocol, '127.0.0.1')
        sep = self._sep

        url = "{protocol}://{host}{sep}{port}".format(
            **locals()
        )

        socket = self._context.socket(socket_type)
        self._CONNECT[bind](socket, url)
        if socket_type in self._INIT:
            self._INIT[socket_type](socket, args)

        return socket

    def log_receiver(self, bind=False):
        return self._sub(self._config['network']['logging'],
                         "log|", bind)

    def log_sender(self):
        return self._pub(self._config['network']['logging'])

    def bus_receiver(self, bind=False):
        return self._sub(self._config['network']['bus'],
                         "petit|", bind)

    def bus_sender(self):
        return self._pub(self._config['network']['bus'])

    def _sub(self, config, filt, bind=False):
        hostname = config.get('host', None)
        return self._create_connection(zmq.SUB, config['port'],
                                       bind, hostname, filt)

    def _pub(self, config):
        hostname = config.get('host', None)
        return self._create_connection(zmq.PUB, config['port'],
                                       False, hostname)
