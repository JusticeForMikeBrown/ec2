#!/usr/bin/env python

__author__ = 'quackmaster@protonmail.com'

import argparse
import boto3
from botocore.exceptions import ClientError

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


# if absent create security group that enables ssh from world
def enable_ssh():

    try:
        check_ssh = [client.describe_security_groups(GroupNames=['ssh'])]
        print(check_ssh)

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
      SecurityGroups=['ssh']
    )

    instances
    print("Created " + args.number + " VMs of type " + args.type)


create_vm()
