#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd $SCRIPT_DIR
sudo apt update -y &&
sudo apt upgrade -y &&
sudo apt install screen -y &&
sudo apt install software-properties-common -y &&
sudo add-apt-repository ppa:deadsnakes/ppa -y &&
sudo apt update -y &&
sudo apt install python3.11 -y &&
curl -sSL https://install.python-poetry.org | python3 - &&
sudo apt install postgresql -y &&
sudo apt --fix-broken install -y
