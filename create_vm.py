#!/usr/bin/env python
import argparse
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import sys
import paramiko
from paramiko import ssh_exception
# import time
import os
import multiprocessing
from joblib import Parallel, delayed


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

# get number of cores
num_cores = multiprocessing.cpu_count()

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
          args.type + " with OS " + args.os + "\n\n")

    now = datetime.now()

    # write created vms to a file
    with open("new_ec2_vms_%s" % now.strftime('%Y-%m-%d-%M'), "w") as f:
        for item in vm_dns:
            f.write("%s\n" % item)

    # print(vm_dns)


get_dns()


def update_kh(vm, vm_dns):

    # print("in create_vm")

    # wait for sshd
    # we can do this or just use while loop below
    # until we get the connection
    # time.sleep(5)

    # for vm in vm_dns:

        # print(vm)

    paramiko.util.log_to_file("aws_ssh.log")

    kh = os.path.expanduser(os.path.join("~", ".ssh", "known_hosts"))

    while True:
        try:
            t = paramiko.Transport(vm, 22)
            t.connect()
        except ssh_exception.SSHException:
            # this will print a lot without the above time.sleep
            # print("problem with ssh connection to " + vm)
            continue
        else:
            print("connected to " + vm + "\n")

        try:
            key = t.get_remote_server_key()
            print("got host key from " + vm + "\n")
        except ssh_exception.SSHException:
            print("failed to get host key from " + vm + "\n")
            continue
        else:
            t.close()
            print("connected closed with " + vm + "\n")

        try:
            hostfile = paramiko.HostKeys(filename=kh)
        except paramiko.hostkeys.HostKeyEntry.InvalidHostKey:
            pass
        else:
            hostfile.add(hostname=vm, key=key, keytype=key.get_name())
            hostfile.save(filename=kh)
            print("added " + vm + " to " + kh + "\n")
            break


#  update_known_hosts()

Parallel(n_jobs=num_cores)(delayed(update_kh)(vm, vm_dns) for vm in vm_dns)


# response = client.describe_instances(Filters=[{'Name': 'instance-state-name',
#                                               'Values': ['pending']}],
#                                     InstanceIds=[])
