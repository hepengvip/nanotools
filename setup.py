from os.path import dirname, realpath, join as path_join
from setuptools import setup, find_packages

from nanotools.version import __version__


package = 'nanotools'
version = __version__


def valid_requirement(line):
    if not line:
        return False
    else:
        ch = line[0]
        return ch not in ('#', '-')


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    root = dirname(realpath(__file__))
    line_iter = (line.strip() for line in open(path_join(root, filename)))
    return [line for line in line_iter if valid_requirement(line)]


setup(
    name=package,
    version=version,
    description='some backend tools',
    author='hepeng',
    author_email='dbt8625@163.com',
    url='https://github.com/hepengvip/nanotools',
    packages=find_packages(exclude=['tests']),
    install_requires=parse_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            f'{package}-webserver = nanotools.entry:start_webapp',
            f'{package}-test = nanotools.script.test:entrance',
        ],
    },
)
