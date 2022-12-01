import paramiko


class ClusterSetup:
    """_summary_
    """

    def __init__(self, instances):
        """_summary_

        Args:
            instances (_type_): _description_
        """
        self.instances = instances
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.key = paramiko.RSAKey.from_private_key_file("labsuser.pem")

    def ssh_execute(self, dns, commands):
        """_summary_

        Args:
            dns (_type_): _description_
            commands (_type_): _description_
        """
        # Connect to instance via SSH
        self.ssh.connect(hostname=dns, username="ubuntu", pkey=self.key)

        # Execute command on instance and unpack stdin, stdout, stderr
        stdin, stdout, stderr = self.ssh.exec_command(commands)

        # Print instance standard output
        while True:
            print(stdout.readline())
            if stdout.channel.exit_status_ready():
                break

    def setup_master(self):
        """_summary_
        """
        SETUP_MASTER = [
            # Prepare directory for MySQL cluster
            'mkdir -p /opt/mysqlcluster/deploy',
            'sudo chmod -R 777 /opt/mysqlcluster',
            'mkdir /opt/mysqlcluster/deploy/conf',
            'mkdir /opt/mysqlcluster/deploy/mysqld_data',
            'mkdir /opt/mysqlcluster/deploy/ndb_data',

            # Setup my.cnf
            '''echo <<EOT >> /opt/mysqlcluster/deploy/my.cnf
            ndbcluster
            datadir=/opt/mysqlcluster/deploy/mysqld_data
            basedir=/opt/mysqlcluster/home/mysqlc
            port=3306
            EOT''',

            # Setup config.ini
            f'''echo <<EOT >> /opt/mysqlcluster/deploy/config.ini
            [ndb_mgmd]
            hostname={self.instances["master"]["public-dns"]}
            datadir=/opt/mysqlcluster/deploy/ndb_data
            nodeid=1

            [ndbd default]
            noofreplicas=3
            datadir=/opt/mysqlcluster/deploy/ndb_data

            [ndbd]
            hostname={self.instances["slave-1"]["public-dns"]}
            nodeid=3

            [ndbd]
            hostname={self.instances["slave-2"]["public-dns"]}
            nodeid=4

            [ndbd]
            hostname={self.instances["slave-3"]["public-dns"]}
            nodeid=5

            [mysqld]
            nodeid=50"
            EOT''',

            # Start the master node
            'sudo /opt/mysqlcluster/home/mysqlc/scripts/mysql_install_db --basedir=/opt/mysqlcluster/home/mysqlc --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data'
            'sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/'
        ]

        self.ssh_execute(self.instances["master"]["public-dns"], SETUP_MASTER)
