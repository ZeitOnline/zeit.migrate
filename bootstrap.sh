#!/bin/bash

virtualenv .
bin/pip install -i http://devpi.zeit.de:4040/zeit/default --trusted-host devpi.zeit.de -e .[test]
bin/pip install pytest-cov pytest-pythonpath pytest-pep8
