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

