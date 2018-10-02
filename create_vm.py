#!/usr/bin/env python

__author__ = 'quackmaster@protonmail.com'

import argparse
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('number', help='number of ec2 instances to create')
parser.add_argument('type', help='type of ec2 instances to create')
print("\nThis script creates EC2 instances - assuming key auth configured.\n")
print("For assistance contact " + __author__ + ".\n")

args = parser.parse_args()

# set ec2 resource var
ec2 = boto3.resource('ec2')

# set client var
client = boto3.client('ec2')

# ssh public key
key = 'id_duckd_donut'


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


# create ec2 vms
def create_vm():
    instances = ec2.create_instances(
      ImageId='ami-04681a1dbd79675a5',
      MinCount=int(1),
      MaxCount=int(args.number),
      InstanceType=args.type,
      SecurityGroups=['ssh'],
      KeyName=key
    )

    instances

    vm_dns = []

    # get public dns of hosts once up
    # then store dns names in a file
    for vm in instances:
        vm.wait_until_running()
        vm.load()
        print(vm.public_dns_name)
        vm_dns.append(vm.public_dns_name)

    print("Created " + args.number + " VMs of type " + args.type)

    now = datetime.now()

    # write created vms to a file
    with open("new_ec2_vms_%s" % now.strftime('%Y-%m-%d-%M'), "w") as f:
        for item in vm_dns:
            f.write("%s\n" % item)


create_vm()


# response = client.describe_instances(Filters=[{'Name': 'instance-state-name',
#                                               'Values': ['pending']}],
#                                     InstanceIds=[])
