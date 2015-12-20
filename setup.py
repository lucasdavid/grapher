from setuptools import setup, find_packages

requirements = [
    'Flask-Script',
    'py2neo',
    'cerberus',
]

test_requirements = [
    'grapher',
    'requests',
    'nose',
    'nose-parameterized',
    'fake-factory',
    'coverage',
    'radon',
    'coveralls'
]

setup(
    name='grapher',
    version='0.1',
    license='MIT',
    url='https://github.com/lucasdavid/grapher',
    author='Lucas David',
    author_email='lucasdavid@drexel.edu',
    description='RESTful APIs creator based on resource schematics.',
    long_description=open('README.md').read(),

    classifiers=[
        'Framework :: Flask-RESTful',
        'Programming Language :: Python',
        'License :: MIT',
        'Natural language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: REST API creator',
    ],

    packages=find_packages(include=('grapher', 'grapher.*')),
    include_package_data=True,

    install_requires=requirements,
    tests_require=test_requirements,
    test_suite='tests'
)
