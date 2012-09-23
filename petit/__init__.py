from pkg_resources import resource_stream

import yaml

def load_config():
    config_file = resource_stream(__package__, "config.yml")
    return yaml.load(config_file)
