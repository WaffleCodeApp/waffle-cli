#!/bin/bash

cd cli
pip3 install --user -r requirements.txt
cd ..

cd sdk
pip3 install --user -r requirements.txt
cd ..
