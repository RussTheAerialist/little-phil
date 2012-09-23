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

def start(system, config):
    # NOTE: Should I even use multiprocessing here?  Probably not
    proc = multiprocessing.Process(target=system, args=(config,))
    proc.start()
    return proc

def main():
    config = petit.load_config()
    processes = [ ]
    comm_factory = communication.factory(config)
    log_receiver = comm_factory.log_receiver(bind=True)
    bus_receiver = comm_factory.bus_receiver(bind=True)
    bus_sender = comm_factory.bus_sender()

    subsystem_status = { }

    for (name, system) in subsystems():
        proc = start(system, config)
        processes.append((name, proc))
        subsystem_status[name] = False

    poller = zmq.Poller()
    poller.register(log_receiver, zmq.POLLIN)
    poller.register(bus_receiver, zmq.POLLIN)

    done = False
    msg_count = 10
    while not done:
        socks = dict(poller.poll())
        for (sock, value) in socks.items():
            if value == zmq.POLLIN:
                message = sock.recv()
                try:
                    packet = packets.Packet.from_string(message)
                    if packet.packet_type == "Sin":
                        response = handshake.Ack.from_sin(packet)
                        bus_sender.send(response.packet)
                        if response._name in subsystem_status:
                            print "{system} Online".format(system=response._name)
                            subsystem_status[response._name] = True

                        # If All of the subsystems are booted, we are done
                        done = reduce(lambda x,y: x and y, subsystem_status.values())
                except Exception, ex:
                    print ex

                msg_count -= 1
                if msg_count <= 0:
                    done = True

    for (name,proc) in processes:
        proc.terminate()

if __name__ == '__main__':
    main()
