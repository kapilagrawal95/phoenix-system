#!/bin/bash
# install python 3.9
sudo add-apt-repository ppa:deadsnakes/ppa; sudo apt update; sudo apt -y install python3.9; sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 2; sudo apt-get -y install python3-pip
# install kubernetes package
sudo apt-get -y install python3.9-distutils; python3 -m pip install kubernetes; python3 -m pip install networkx; python3 -m pip install numpy; python3 -m pip install requests
kubectl label node node-4 nodes=4
kubectl label node node-1 nodes=1
kubectl label node node-0 nodes=0
kubectl label node node-3 nodes=3
kubectl label node node-2 nodes=2
