from EC2_instances_creator import EC2Creator

ec2 = EC2Creator()

# Launching 5 instances and storing their information in the
# instances dict as follows :
# {
#   "stand-alone": {
#       "instance": ...
#       "private-dns": ...
#       "public-dns": ...
#       "ipv4": ...
#   }
#   "master": {...}
#   "slave-1": {...}
#   ...
# }
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
