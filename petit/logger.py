import logging

class ZmqLogHandler(logging.Handler):
    def __init__(self, zmq_socket, level=logging.NOTSET):
        super(ZmqLogHandler, self).__init__(level)
        self._socket = zmq_socket
        self.setFormatter(logging.Formatter("log|%(name)s|%(module)s|%(lineno)d|%(msg)s"))

    def emit(self, record):
        self._socket.send(self.format(record))
