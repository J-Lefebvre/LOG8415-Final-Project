#!/bin/bash

### slave.sh automates the setup of a slave node of a MySQL cluster ###

# 1. Create destination folder for MySQL
sudo mkdir -p /opt/mysqlcluster/home
sudo chmod -R 777 /opt/mysqlcluster

# 2. Download and unpack MySQL to /opt/mysqlcluster/home/
wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz -P /opt/mysqlcluster/home/
tar -xvf /opt/mysqlcluster/home/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz -C /opt/mysqlcluster/home/
ln -s /opt/mysqlcluster/home/mysql-cluster-gpl-7.2.1-linux2.6-x86_64 /opt/mysqlcluster/home/mysqlc

# 3. Add MYSQLC_HOME to PATH
sudo chmod -R 777 /etc/profile.d
echo "export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc" >> /etc/profile.d/mysqlc.sh
echo "export PATH=$MYSQLC_HOME/bin:$PATH" >> /etc/profile.d/mysqlc.sh

# 4. Install libncurses5 on the instance
source /etc/profile.d/mysqlc.sh
sudo apt-get update && sudo apt-get -y install libncurses5

# 5. Install sysbench
sudo apt-get -y install sysbench