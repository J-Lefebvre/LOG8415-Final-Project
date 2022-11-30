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
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.key = paramiko.RSAKey.from_private_key_file("key.pem")

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

