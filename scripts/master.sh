#!/bin/bash

### master.sh automates the setup of the master node of a MySQL cluster ###

# 1. Install mysql-server
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install mysql-server
