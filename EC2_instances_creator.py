import json
import string
import boto3
import common
import time


class EC2Creator:
    def __init__(self):
        self.client = boto3.client('ec2')
        self.open_http_port()
        self.instance_id = None

    # Runs a request to create an instance from parameters and saves their ids
    def create_instance(self, availability_zone, instance_type):
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
            # UserData=open('launch_script.sh').read()
        )
        print(response["Instances"][0]["InstanceId"])
        time.sleep(5)
        return response["Instances"][0]

    # Termination function that terminates the running instance
    def terminate_instance(self):
        self.client.terminate_instances(InstanceIds=[self.instance_id])

    # If not done already, opens the port 80 on the default security group so
    #  the ports of all instances and they are exposed by default on creation
    def open_http_port(self):
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
        Instances = {
            "stand-alone": {},
            "master": {},
            "slave-1": {},
            "slave-2": {},
            "slave-3": {},
        }

        # Create instances
        Instances["stand-alone"]["instance"] = self.create_instance(
            common.US_EAST_1A, common.T2_MICRO)
        Instances["master"]["instance"] = self.create_instance(
            common.US_EAST_1A, common.T2_MICRO)
        for instance in range(1, 4):
            Instances[f"slave-{instance}"]["instance"] = self.create_instance(
                common.US_EAST_1A, common.T2_MICRO)

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
            id (_type_): id of the instance to wait on
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
