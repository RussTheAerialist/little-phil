import multiprocessing
import os.path as path
from pkg_resources import resource_listdir

import petit

def load(module_name):
    try:
        full_module_name = "petit.{module_name}".format(module_name=module_name)
        module = __import__(full_module_name)
        main_module = getattr(module, module_name, None)
        if main_module is None:
            return None

        function = getattr(main_module, 'main', None)
        if function is None:
            return None

        return function
    except ImportError:
        return None

def subsystems():
    for system in filter(lambda x: x.endswith("_subsystem.py"),
                         resource_listdir('petit', '')):
        (module_name, _) = path.splitext(system)
        retval = load(module_name)
        if retval is not None:
            yield (module_name, retval)

def start(system, config):
    proc = multiprocessing.Process(target=system, args=(config,))
    proc.start()
    return proc

def main():
    config = petit.load_config()
    processes = [ ]
    for (name, system) in subsystems():
        proc = start(system, config)
        processes.append(proc)

    for proc in processes:
        proc.join()

if __name__ == '__main__':
    main()
