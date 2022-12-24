import time
import paramiko


class ClusterSetup:
    """Helper class to setup the MySQL Cluster 
    """

    def __init__(self, instances):
        """Store instances structure and prepare paramiko (SSH)

        Args:
            instances: information on instances
        """
        self.instances = instances
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.key = paramiko.RSAKey.from_private_key_file("labsuser.pem")

    def ssh_execute(self, dns, commands, output_file=""):
        """Connect to specified instance using SSH, run provided commands and print output to console (or specified file) 

        Args:
            dns: instance to connect to
            commands: commands to run
        """
        # Connect to instance via SSH
        self.ssh.connect(hostname=dns, username="ubuntu", pkey=self.key)

        # Execute command on instance and unpack stdin, stdout, stderr
        for command in commands:
            stdin, stdout, stderr = self.ssh.exec_command(command)

            # Save output of the commands to specified filename
            if output_file != "":
                output = open(f'{output_file}.txt', 'a+')
                output.write(" ".join(stdout.readlines()))
                output.close()
            else:
                print(f"{dns} : {command}")
                print(stdout.readlines())

    def start_cluster(self):
        """Entry function to setup the MySQL cluster
        """
        print("Setting up master...")
        self.setup_master()
        time.sleep(15)
        print("Starting slaves...")
        self.start_slaves()
        time.sleep(15)
        print("Starting master...")
        self.start_master()
        time.sleep(200)
        self.use_sakila_master()

    def setup_master(self):
        """Setup of MySQL on the master instance, populating the my.cnf and config.ini files
        """
        SETUP_MASTER = [
            # Prepare directory for MySQL cluster
            'mkdir -p /opt/mysqlcluster/deploy',
            'sudo chmod -R 777 /opt/mysqlcluster',
            'mkdir /opt/mysqlcluster/deploy/conf',
            'mkdir /opt/mysqlcluster/deploy/mysqld_data',
            'mkdir /opt/mysqlcluster/deploy/ndb_data',

            # Setup my.cnf
            '''echo "[mysqld]
ndbcluster
datadir=/opt/mysqlcluster/deploy/mysqld_data
basedir=/opt/mysqlcluster/home/mysqlc
port=3306" > /opt/mysqlcluster/deploy/my.cnf''',

            # Setup config.ini
            f'''echo "[ndb_mgmd]
hostname={self.instances["master"]["private-dns"]}
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=1

[ndbd default]
noofreplicas=3
datadir=/opt/mysqlcluster/deploy/ndb_data

[ndbd]
hostname={self.instances["slave-1"]["private-dns"]}
nodeid=3

[ndbd]
hostname={self.instances["slave-2"]["private-dns"]}
nodeid=4

[ndbd]
hostname={self.instances["slave-3"]["private-dns"]}
nodeid=5

[mysqld]
nodeid=50" > /opt/mysqlcluster/deploy/config.ini'''
        ]
        self.ssh_execute(self.instances["master"]["public-dns"], SETUP_MASTER)

    def start_slaves(self):
        """Start MySQL on each slave node and links them to the master node
        """
        START_SLAVES = [
            'mkdir -p /opt/mysqlcluster/deploy/ndb_data',
            f'/opt/mysqlcluster/home/mysqlc/bin/ndbd -c {self.instances["master"]["public-dns"]}'
        ]
        for i in range(1, 4):
            self.ssh_execute(
                self.instances[f"slave-{i}"]["public-dns"], START_SLAVES)

    def start_master(self):
        """Start MySQL on the master node
        """
        START_MASTER = [
            # Start the master node
            'cd ../..',
            '/opt/mysqlcluster/home/mysqlc/scripts/mysql_install_db --basedir=/opt/mysqlcluster/home/mysqlc --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data',
            '/opt/mysqlcluster/home/mysqlc/bin/ndb_mgmd -f /opt/mysqlcluster/deploy/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/',
            '/opt/mysqlcluster/home/mysqlc/bin/mysqld --defaults-file=/opt/mysqlcluster/deploy/my.cnf --user=root &'
        ]
        self.ssh_execute(
            self.instances["master"]["public-dns"], START_MASTER)

    def use_sakila_master(self):
        """Creates a User, installs Sakila, adds it to MySQL and starts using Sakila.
        """
        SAKILA_MASTER = [
            # Create User
            '''sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -e "CREATE USER 'myapp'@'%' IDENTIFIED BY 'testpwd';GRANT ALL PRIVILEGES ON * . * TO 'myapp'@'%' IDENTIFIED BY 'password' WITH GRANT OPTION MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0 ;"''',
            '''sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -e "USE mysql; UPDATE user SET plugin='mysql_native_password' WHERE User='root'; FLUSH PRIVILEGES;SET PASSWORD FOR 'root'@'localhost' = PASSWORD('password');"''',

            # Install Sakila
            'wget https://downloads.mysql.com/docs/sakila-db.tar.gz',
            'tar -xvf sakila-db.tar.gz',

            # Add Sakila onto MySQL and use Sakila
            '''/opt/mysqlcluster/home/mysqlc/bin/mysql -h 127.0.0.1 -e "SOURCE sakila-db/sakila-schema.sql;" -u root -ppassword''',
            '''/opt/mysqlcluster/home/mysqlc/bin/mysql -h 127.0.0.1 -e "SOURCE sakila-db/sakila-data.sql;" -u root -ppassword''',
            '''/opt/mysqlcluster/home/mysqlc/bin/mysql -h 127.0.0.1 -e "USE sakila;" -u root -ppassword'''
        ]
        self.ssh_execute(
            self.instances["master"]["public-dns"], SAKILA_MASTER)

    def run_benchmark(self):
        """Benchmarks MySQL stand-alone and the cluster with sysbench 
        """
        RUN_BENCHMARK = [
            # Generate a table to run the benchmarking on
            'sudo sysbench oltp_read_only --table-size=1000000 --mysql-db=sakila --mysql-user=root --mysql-password=password --mysql-socket=\"/var/run/mysqld/mysqld.sock\" prepare',
            # Run performance tests
            'sudo sysbench --histogram oltp_read_only --table-size=1000000 --threads=6 --max-time=60 --max-requests=0 --mysql-db=sakila --mysql-user=root --mysql-password=password --mysql-socket=\"/var/run/mysqld/mysqld.sock\" run',
            # Drop the benchmarking table
            'sudo sysbench oltp_read_only --mysql-db=sakila --mysql-user=root --mysql-password=password --mysql-socket=\"/var/run/mysqld/mysqld.sock\" cleanup',
        ]
        self.ssh_execute(
            self.instances["master"]["private-dns"], RUN_BENCHMARK, "benchmark_output_master")
        self.ssh_execute(
            self.instances["stand-alone"]["private-dns"], RUN_BENCHMARK, "benchmark_output_standalone")
