import logging

import zmq

import petit.lib as lib
import petit.logger as logger
import petit.communication as communication
import petit.packets.handshake as handshake

class Subsystem(lib._BaseObject):
    def __init__(self, config, name, log):
        super(Subsystem, self).__init__(config)
        self._name = name
        self._comm_factory = communication.factory(self._config)
        self._bus_sender = self._comm_factory.bus_sender()
        self._bus_receiver = self._comm_factory.bus_receiver()
        self._log_sender = self._comm_factory.log_sender()
        self._log = log
        self._log.addHandler(logger.ZmqLogHandler(self._log_sender, logging.DEBUG))

    def start(self):
        self._handshake()
        self.run()

    def _handshake(self):
        handshake_complete = False
        sin = handshake.Sin(name=self._name)

        poller = zmq.Poller()
        poller.register(self._bus_receiver, zmq.POLLIN)

        while not handshake_complete:
            self._bus_sender.send(sin.packet)
            socks = dict(poller.poll(1000))
            if self._bus_receiver in socks:
                data = self._bus_receiver.recv()
                ack = handshake.Ack.from_string(data)
                if ack.guid == sin.guid:
                    handshake_complete = True

