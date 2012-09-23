import logging
log = logging.getLogger(__name__)

import zmq

import petit.lib.subsystem as subsystem

class HardwareSubsystem(subsystem.Subsystem):
    def run(self):
        pass

def main(config):
    log.setLevel(logging.DEBUG)
    subsystem = HardwareSubsystem(config, __name__, log)
    subsystem.start()

    print "done"

if __name__ == '__main__':
    import yaml

    main(yaml.load(open("config.yml")))
