#!/bin/bash

virtualenv .
bin/pip install -i https://devpi.zeit.de/zeit/default -e .[test]
bin/pip install pytest-cov pytest-pythonpath pytest-pep8
