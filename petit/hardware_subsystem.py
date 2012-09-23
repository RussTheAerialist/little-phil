import logging
log = logging.getLogger(__name__)

import zmq

import petit.communication as communication
import petit.logger as logger

def main(config):
    comm_factory = communication.factory(config)
    zmq_logger = comm_factory.log_sender()
    log.setLevel(logging.DEBUG)

    log.addHandler(logger.ZmqLogHandler(zmq_logger, logging.DEBUG))

    log.info("Hardware Subsystem Online")
    print "done"

if __name__ == '__main__':
    import yaml

    main(yaml.load(open("config.yml")))
