import zmq

def main(config):
    context = zmq.Context()
    bus_recv = zmq.socket(zmq.SUB)
    bus_recv.connect("tcp://localhost:{port}".format(port=config['network']['bus']['recv']))
    bus_recv.setsockopt(zmq.SUBSCRIBE, 'cmd:')

    bus_send = zmq.socket(zmq.PUB)
    bus_send.connect("tcp://localhost:{port}".format(port=config['network']['bus']['send']))

    print "Hardware Subsystem Online"
