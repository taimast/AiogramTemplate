#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd $SCRIPT_DIR
sudo apt update && sudo apt upgrade -y
sudo apt install screen -y
sudo apt install software-properties-common -y
echo | sudo add-apt-repository ppa:deadsnakes/ppa -y
# sudo add-apt-repository ppa:deadsnakes/ppa
# yes "" | sudo add-apt-repository ppa:deadsnakes/ppa -y
# echo -ne '\n' | sudo add-apt-repository ppa:deadsnakes/ppa
# sudo add-apt-repository ppa:deadsnakes/ppa

sudo apt update -y && sudo apt install python3.10 -y && sudo apt install python3.10-venv -y
sudo apt-get install python3.10-distutils -y
sudo apt-get install python3.8-distutils -y
sudo apt-get install python-dev-tools -y
sudo apt-get install python3-dev -y
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3.10 -
poetry install --no-dev
sudo apt --fix-broken install -y
sudo apt-get install build-essential