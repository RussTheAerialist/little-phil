import uuid

import petit.packets as packets

class Sin(packets.Packet):
    def _init(self, **kargs):
        super(Sin, self)._init(**kargs)
        if 'guid' not in kargs:
            x = uuid.uuid5(uuid.NAMESPACE_DNS, type(self).__name__)
            self.guid = x.hex

    def _packet(self):
        return { 'guid': self.guid }

class Ack(packets.Packet):
    @classmethod
    def from_sin(cls, sin_packet):
        retval = Ack(sin_packet._message_type,
                     sin_packet._name,
                     guid=sin_packet.guid)
        return retval

    def _packet(self):
        return { 'guid': self.guid }

