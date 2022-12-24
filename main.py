from instances_creator import InstancesCreator
from cluster_setup import ClusterSetup

ec2 = InstancesCreator()

# Creates a stand-alone node, a master node and three slave nodes.
# The nodes are instantiated with the UserData in the /scripts folder
print('Creating instances...')
instances = ec2.create_instances()
print('Instances created.')

# Prints information on each instance
for instance in instances:
    print(instance)
    print(f"\tid: {instances[instance]['id']}")
    print(f"\tprivate-dns: {instances[instance]['private-dns']}")
    print(f"\tpublic-dns: {instances[instance]['public-dns']}")
    print(f"\tipv4: {instances[instance]['ipv4']}")

# Setup and start the MySQL cluster using the ClusterSetup class
cs = ClusterSetup(instances)
cs.start_cluster()

# Benchmark MySQL stand-alone and cluster
cs.run_benchmark()

# Terminate services
# ec2.terminate_instance()
