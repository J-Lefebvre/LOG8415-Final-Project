import json
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
print(print(json.dumps(Instances,
                       sort_keys=False, indent=4, default=str)))


# Terminate services
# ec2.terminate_instance()
