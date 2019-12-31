#!/bin/bash
set -e

MY_PATH=${PWD}

cd ${MY_PATH}
rm -rf ${MY_PATH}/venv
trap 'rm -rf "${MY_PATH}/venv"' EXIT

cd ${MY_PATH}
python3 -m venv ${MY_PATH}/venv
. ${MY_PATH}/venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt

cd ${MY_PATH}
python3 _build_site.py
