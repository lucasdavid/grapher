from setuptools import setup, find_packages

setup(
    name='demosthenes',
    version='0.1',
    license='MIT',
    long_description=open('README.md').read(),
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    install_requires=['neomodel'],
    extras_require={'tests': ['fake-factory', 'nose', 'nose-parameterized', 'coverage', 'radon']},
    test_suite='tests.unit',
    classifiers=[
        'Programming Language :: Python',
        'License :: MIT',
        'Natural language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: Education',
    ],
)
