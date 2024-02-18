#!/bin/bash

pip3 freeze --user | xargs pip3 uninstall -y
