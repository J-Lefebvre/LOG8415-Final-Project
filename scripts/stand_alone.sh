#!/bin/bash

### stand_alone.sh automates the setup of MySQL stand-alone on a Linux node. ###

# 1. Install mysql-server
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install mysql-server

# 2. Install Sakila
wget https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xf sakila-db.tar.gz

# 3. Create the DB structure
sudo mysql -e "SOURCE sakila-db/sakila-schema.sql;"

# 4. Populate the database
sudo mysql -e "SOURCE sakila-db/sakila-data.sql;"

# 5. Begin using the database
sudo mysql -e "USE sakila;"

# 6. Install sysbench
sudo apt-get -y install sysbench