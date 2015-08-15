# SETUP

## Introduction
This file describes the development setup process for this project

## Step-stones

1. Have [python-3.4](https://www.python.org/) and [neo4j](http://neo4j.com/) installed. If you're running
 on [Ubuntu](http://www.ubuntu.com/) or any ubuntu-based operating system, you may skip python installation.
2. Clone Grapher repository
```
git clone https://github.com/lucasdavid/grapher
```
2. Install the project
```shell
cd path/to/grapher
python setup.py install
```
3. Finally, run the embedded server
```shell
python manage.py runserver
```
