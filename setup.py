from setuptools import setup

setup(
    name='seed',
    version='0.0.1',
    description='The SEED client',
    author='Orivej Desh',
    author_email='orivej@gmx.fr',
    license='Unlicense',
    url='https://github.com/orivej/pyseed',
    packages=['seed'],
    install_requires=['attrs', 'requests', 'PyYAML'],
)
