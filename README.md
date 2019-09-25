# Deepengine Project
This project provides a bridge into Kerbal Space Program so that you can control your ship with a deep learning network.

## Objectives
* Provide and share knowledge with everyone
* Create and innovative new deep learning networks
* Excite people to join and have fun


## Overview
This project is broken into several sections.

* KSP Plugin - A plugin for KSP that will read and transmit game state to a python library.
* Notebooks and Challenges - Challenges are a set of goals/objectives you want your network to achieve.
* Agents - An agent is a provided network that can be used and modified.

## Getting Started
The first step is to clone this repo.

'''
git clone https://github.com/MDBox/ksp-deepengine.git
'''

### KSP Plugin - DeepEngine
The DeepEngine plugin is a Unity plugin that takes over control of KSP as soon as the game is launched. It might be a good idea to have a separate game directory just for this plugin. *You will need to remove the plugin if you wish to play the game normally.*

* This plugin will only work on Linux and OSX because they support 'FIFO' pipes.  

#### Install Plugin

'''
cp -r ./deep_engine /path/to/ksp/Plugins/
'''




### Setup Jupyter Notebook
To use the notebooks you should first create a Python3 virtual environment and install the requirements.

'''
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
'''

You can now start Jupyter Notebook with this command. It should automatically open your web browser to the notebook server.

'''
jupyter-lab
'''

## Start Challenge 1
The first challenge is already setup with a basic example. I think it can be improved!

* [First Challenge](https://github.com/MDBox/ksp-deepengine/tree/master/challenges/challenge1/Challenge1.ipynb)
