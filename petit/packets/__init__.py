import json
import logging
import types
log = logging.getLogger(__name__)

import petit.lib as lib

_packet_registry = None

def PacketRegistry():
    """ This is a lazy singleton implementation """
    global _packet_registry

    def class_finder(parent_class):
        for (name, module) in lib.glob_modules('petit.packets', lambda x: not x.endswith('__init__.py')):
            for x in [getattr(module, y) for y in dir(module)]:
                if types.TypeType == type(x) and issubclass(x, parent_class):
                    yield (x.__name__, x)

    if _packet_registry is not None:
        return _packet_registry

    _packet_registry = dict([x for x in class_finder(Packet)])
    return _packet_registry

class Packet(object):
    def __init__(self, message_type = 'petit', name = 'Global', **kargs):
        self._message_type = message_type
        self._name = name
        self._init(**kargs)

    def _init(self, **kargs):
        self.__dict__.update(kargs)

    @property
    def packet_type(self):
        return type(self).__name__

    @property
    def packet(self):
        packet_type = self.packet_type
        data = self._packet()
        packet_data = json.dumps(data)

        return "{message_type}|{packet_type}|{name}|{packet_data}".format(
            message_type = self._message_type,
            name = self._name,
            **locals()
        )

    @classmethod
    def from_string(self, packet):
        (message_type, packet_type, name, data) = packet.split("|", 3)
        registry = PacketRegistry()
        if packet_type not in registry:
            log.warning("Unknown Packet Name: %s on %s", name, message_type)
            raise Exception("Unknown Packet Type: %s on %s" % (name, message_type))

        data = json.loads(data)
        retval = registry[packet_type](message_type, name=name, **data)

        return retval
