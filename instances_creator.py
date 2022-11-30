import boto3
import common
import time


class InstancesCreator:
    """Responsible for creating the instances required for the Final Project
    """

    def __init__(self):
        """Initializes the boto3 client
        """
        self.client = boto3.client('ec2')
        self.open_http_port()

    def create_instance(self, availability_zone, instance_type, script):
        """Runs a request to create an instance from parameters

        Args:
            availability_zone (string): AWS Availability Zone
            instance_type (string): AWS Instance Type

        Returns:
            dict: instance resources
        """
        response = self.client.run_instances(
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        # deleting the storage on instance termination
                        'DeleteOnTermination': True,

                        # 8gb volume
                        'VolumeSize': 8,

                        # Volume type
                        'VolumeType': 'gp2',
                    },
                },
            ],

            # UBUNTU instance
            ImageId=common.UBUNTU_IMAGE,

            # UBUNTU instance
            InstanceType=instance_type,

            # Availability zone
            Placement={
                'AvailabilityZone': availability_zone,
            },

            DisableApiTermination=False,

            # One instance
            MaxCount=1,
            MinCount=1,

            # Script to launch on instance startup
            UserData=open(script).read()
        )
        print(response["Instances"][0]["InstanceId"])
        time.sleep(5)
        return response["Instances"][0]

    def terminate_instance(self):
        """Termination function that terminates the running instance
        """
        self.client.terminate_instances(InstanceIds=[self.instance_id])

    def open_http_port(self):
        """Opens the port 80 on the default security group so
           the ports of all instances are exposed by default on creation
        """
        # Gets all open ports on the default group
        opened_ports = [i_protocol.get('FromPort') for i_protocol in
                        self.client.describe_security_groups(
                            GroupNames=[common.DEFAULT_SECURITY_GROUP_NAME])
                        ['SecurityGroups'][0]['IpPermissions']]
        # if HTTP port not already open, open it
        if common.HTTP_PORT not in opened_ports:
            self.client.authorize_security_group_ingress(
                GroupName=common.DEFAULT_SECURITY_GROUP_NAME,
                CidrIp=common.CIDR_IP,
                FromPort=common.HTTP_PORT,
                ToPort=common.HTTP_PORT,
                IpProtocol=common.IP_PROTOCOL
            )

    def create_instances(self):
        """Creates the instances required for the final project

        Returns:
            dict: contains information on the instances as follows :
            {
            "stand-alone": {
                "instance": {...}
                "id": "i-085c88c0f0d66e1c9"
                "private-dns": "ip-172-31-35-29.ec2.internal"
                "public-dns": "ec2-18-206-201-84.compute-1.amazonaws.com"
                "ipv4": "18.206.201.84"
            }
            "master": {...}
            "slave-1": {...}
            "slave-2": {...}
            "slave-3": {...}
            }
        """
        Instances = {
            "stand-alone": {},
            "master": {},
            "slave-1": {},
            "slave-2": {},
            "slave-3": {},
        }

        # Create instances
        Instances["stand-alone"]["instance"] = self.create_instance(
            common.US_EAST_1A, common.T2_MICRO, common.STAND_ALONE_SCRIPT)
        Instances["master"]["instance"] = self.create_instance(
            common.US_EAST_1A, common.T2_MICRO, common.MASTER_SCRIPT)
        for instance in range(1, 4):
            Instances[f"slave-{instance}"]["instance"] = self.create_instance(
                common.US_EAST_1A, common.T2_MICRO, common.SLAVE_SCRIPT)

        # Retrieve and store instances information
        for instance_key in Instances:
            id = Instances[instance_key]["instance"]["InstanceId"]
            Instances[instance_key]["id"] = id

            self.wait_for_instance(id)

            Instances[instance_key]["private-dns"] = Instances[instance_key]["instance"]["PrivateDnsName"]

            reservations = self.client.describe_instances(
                InstanceIds=[id]).get("Reservations")

            for reservation in reservations:
                for instance in reservation['Instances']:
                    public_dns = instance.get("PublicDnsName")
                    public_ip = instance.get("PublicIpAddress")

            Instances[instance_key]["public-dns"] = public_dns
            Instances[instance_key]["ipv4"] = public_ip

        return Instances

    def wait_for_instance(self, id):
        """Sleeps until the instance with the provided id is running (60s timeout)

        Args:
            id (string): id of the instance to wait on
        """
        counter = 0
        while True:
            response = self.client.describe_instance_status(
                InstanceIds=[id])
            counter += 1
            try:
                status = response["InstanceStatuses"][0]["InstanceState"]["Name"]
                if status == "running":
                    break
            except:
                pass
            if counter > 11:
                break
            time.sleep(5)
