from setuptools import setup, find_packages

requirements = []
try:
    with open('requirements.txt') as f:
        requirements += f.readlines()
except IOError:
    pass

dev_requirements = requirements[:]
try:
    with open('requirements-dev.txt') as f:
        dev_requirements += f.readlines()
except IOError:
    pass

setup(
    name='grapher',
    version='0.1',
    license='MIT',
    long_description=open('README.md').read(),
    packages=find_packages(include=('grapher', 'grapher.*')),
    include_package_data=True,

    install_requires=requirements,

    test_requires=dev_requirements,
    test_suite='tests.unit',

    classifiers=[
        'Programming Language :: Python',
        'License :: MIT',
        'Natural language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: REST API creator',
    ],
)
