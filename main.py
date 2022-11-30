from instances_creator import InstancesCreator

ec2 = InstancesCreator()

print('Creating instances...')
Instances = ec2.create_instances()
print('Instance created.')

for instance in Instances:
    print(instance)
    print(f"\tid: {Instances[instance]['id']}")
    print(f"\tprivate-dns: {Instances[instance]['private-dns']}")
    print(f"\tpublic-dns: {Instances[instance]['public-dns']}")
    print(f"\tipv4: {Instances[instance]['ipv4']}")

# Terminate services
# ec2.terminate_instance()
