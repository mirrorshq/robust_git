#!/bin/bash

FILES="$(find python3/robust_layer -name '*.py' | tr '\n' ' ')"
autopep8 -ia --ignore=E402,E501 ${FILES}
