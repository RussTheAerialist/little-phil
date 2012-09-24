import multiprocessing
import os.path as path
from pkg_resources import resource_listdir

import zmq

import petit
import petit.lib as lib
import petit.communication as communication
import petit.packets as packets
import petit.packets.handshake as handshake

def subsystems():
    for (name, module) in lib.glob_modules("petit", lambda x: x.endswith("_subsystem.py")):
        name = "petit.{name}".format(name=name)
        function = getattr(module, 'main', None)
        if function is not None:
            yield (name, function)

def camelcase(string):
    if string.count("_") == 0:
        return string.capitalize()
    return "".join([x.capitalize() for x in string.split("_")])

def event_camelcase(string):
    return camelcase(string.replace("_event", ""))

def get_responders():
    """ Get all event handlers in the current module """
    retval = dict([(event_camelcase(x),y) for (x,y) in globals().items() if x.endswith('event')])
    return retval

def start(system, config):
    # NOTE: Should I even use multiprocessing here?  Probably not
    proc = multiprocessing.Process(target=system, args=(config,))
    proc.start()
    return proc

def sin_event(packet, status):
    response = handshake.Ack.from_sin(packet)
    if response._name in status:
        print "{system} Online".format(system=response._name)
        retval = dict(status)
        retval[response._name] = True

        return (response, retval)
    return (None, None)

def main():
    config = petit.load_config()
    processes = [ ]
    comm_factory = communication.factory(config)
    log_receiver = comm_factory.log_receiver(bind=True)
    bus_receiver = comm_factory.bus_receiver(bind=True)
    bus_sender = comm_factory.bus_sender()

    responders = get_responders()

    subsystem_status = { }

    for (name, system) in subsystems():
        proc = start(system, config)
        processes.append((name, proc))
        subsystem_status[name] = False

    poller = zmq.Poller()
    poller.register(log_receiver, zmq.POLLIN)
    poller.register(bus_receiver, zmq.POLLIN)

    done = False
    while not done:
        socks = dict(poller.poll())
        for (sock, value) in socks.items():
            if value == zmq.POLLIN:
                message = sock.recv()
                try:
                    packet = packets.Packet.from_string(message)
                    if packet.packet_type in responders:
                        responder = responders[packet.packet_type]
                        (response, status) = responder(packet, subsystem_status)
                        if response is not None:
                            bus_sender.send(response.packet)
                            subsystem_status = status

                        done = reduce(lambda x,y: x and y, subsystem_status.values())
                except Exception, ex:
                    print ex

    for (name,proc) in processes:
        proc.terminate()

if __name__ == '__main__':
    main()
