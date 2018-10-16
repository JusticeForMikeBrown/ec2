#!/usr/bin/env python
import argparse
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import sys
import paramiko

__author__ = 'quackmaster@protonmail.com'

parser = argparse.ArgumentParser()
parser.add_argument('number', help='number of ec2 instances to create')
parser.add_argument('type', help='type of ec2 instances to create')
parser.add_argument('os', help='operating system for ec2 instances')
print("\nThis script creates EC2 instances - assuming key auth configured.\n")
print("For assistance contact " + __author__ + ".\n")

args = parser.parse_args()

# set ec2 resource var
ec2 = boto3.resource('ec2')

# set client var
client = boto3.client('ec2')

# ssh public key
ssh_key = 'id_duckd_donut'


# if absent create security group that enables ssh from world
def enable_ssh():

    try:
        check_ssh = [client.describe_security_groups(GroupNames=['ssh'])]
        # print(check_ssh)

    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidGroup.NotFound':
            print("Creating SSH Security Group")
            ssh = ec2.create_security_group(GroupName='ssh', Description='SSH')
            ssh.authorize_ingress(IpProtocol="tcp", CidrIp="0.0.0.0/0",
                                  FromPort=22, ToPort=22)
        pass


enable_ssh()


# ensure proper operating system selected
def get_vm_os():

    ami = {'amazon': 'ami-04681a1dbd79675a5',
           'ubuntu': 'ami-0ac019f4fcb7cb7e6',
           'rhel': 'ami-6871a115'}

    global vm_os

    vm_os = []

    for key, value in ami.items():
        if args.os in key:
            vm_os.append(value)
            return vm_os
        else:
            print("Invalid operating system selected")
            sys.exit()


get_vm_os()


# only allow vm types defined in below list
def get_vm_type():

    types = ['t3.nano', 't3.micro', 't3.small']

    global ec2_type

    ec2_type = []
    for item in types:
        if args.type == item:
            ec2_type.append(item)
            return ec2_type
        else:
            print("Invalid EC2 type selected")
            sys.exit()


get_vm_type()


# create ec2 vms
def create_vm():

    global instances

    instances = ec2.create_instances(
      ImageId=str(vm_os[0]),
      MinCount=int(1),
      MaxCount=int(args.number),
      InstanceType=str(ec2_type[0]),
      SecurityGroups=['ssh'],
      KeyName=ssh_key
    )

    instances

create_vm()


def get_dns():

    global vm_dns

    vm_dns = []

    # get public dns of hosts once up
    # then store dns names in a file
    for vm in instances:
        vm.wait_until_running()
        vm.load()
        # print(vm.public_dns_name)
        vm_dns.append(vm.public_dns_name)

    print("Created " + args.number + " VMs of type " +
          args.type + " with OS " + args.os)

    now = datetime.now()

    # write created vms to a file
    with open("new_ec2_vms_%s" % now.strftime('%Y-%m-%d-%M'), "w") as f:
        for item in vm_dns:
            f.write("%s\n" % item)

    # print(vm_dns)

get_dns()


def update_known_hosts():

    print("in create_vm")
    # functions return none
    # though create_vm() will return list of vms
    # using this instead of global var
    for vm in vm_dns:

        print(vm)

        known_hosts = '~/.ssh/known_hosts'
        port = '22'

        transport = paramiko.Transport(vm, port)
        print("transport defined")
        transport.connect(password=None, pkey=None)
        print("connection created")
        key = transport.get_remote_server_key()
        print("key defined")
        transport.close()
        print("connection closed")
        hostfile = paramiko.HostKeys(filename=known_hosts)
        hostfile.add(hostname=vm, key=key, keytype=key.get_name())
        hostfile.save(filename=known_hosts)
        print(known_hosts + " updated")

update_known_hosts()


# response = client.describe_instances(Filters=[{'Name': 'instance-state-name',
#                                               'Values': ['pending']}],
#                                     InstanceIds=[])
