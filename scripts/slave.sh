#!/bin/bash

### slave.sh automates the setup of a slave node of a MySQL cluster ###

# 1. Install mysql-server
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install mysql-server
