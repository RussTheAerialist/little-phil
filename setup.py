from setuptools import setup

setup(
    name = "PetitPhilippe",
    version = "0.1",
    packages = [
        "petit",
        "petit.lib",
        "petit.packets",
    ],
    scripts = [
        "boot.py",
    ],
    package_data = {
        '': [ '*.yml' ]
    },
    install_requires = [
        "pyzmq",
        "pyyaml",
    ],
    dependency_links = [
        "https://bitbucket.org/tino/pyfirmata/get/4bed4280dd31.tar.gz"
    ],

    author = "Russell Hay",
    author_email = "me@russellhay.com",
    description = "Robotic Brain for a Balance bot",
    license = "PSF",
    keywords = "arduino robot",
    url = "http://russellhay.com/t/petit",
)
