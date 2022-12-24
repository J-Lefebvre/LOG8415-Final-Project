from instances_creator import InstancesCreator
from cluster_setup import ClusterSetup

ec2 = InstancesCreator()

print('Creating instances...')
instances = ec2.create_instances()
print('Instances created.')

for instance in instances:
    print(instance)
    print(f"\tid: {instances[instance]['id']}")
    print(f"\tprivate-dns: {instances[instance]['private-dns']}")
    print(f"\tpublic-dns: {instances[instance]['public-dns']}")
    print(f"\tipv4: {instances[instance]['ipv4']}")

cs = ClusterSetup(instances)
cs.start_cluster()

cs.run_benchmark()

# Terminate services
# ec2.terminate_instance()
