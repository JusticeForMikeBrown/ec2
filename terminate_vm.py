#!/usr/bin/env python
import boto3
import argparse

__author__ = 'quackmaster@protonmail.com'

parser = argparse.ArgumentParser()
parser.add_argument('terminate',  nargs='?', default=False, type=bool,
                    help='remove all EC2 VMs')
print("\nThis script terminates all EC2 instances. \n")
print("For assistance contact " + __author__ + ".\n")

args = parser.parse_args()


# set ec2 resource var
ec2 = boto3.resource('ec2')


def get_vms():
    instances = ec2.instances.filter(
                 Filters=[{'Name': 'instance-state-name',
                           'Values': ['running']}])
    global vms
    vms = []

    for vm in instances:
        vms.append(vm.id)

    # print(vms)


get_vms()


def terminate_vms(vms):

    if args.terminate:
        # remove all ec2 instances
        ec2.instances.filter(InstanceIds=vms).terminate()

        for vm in vms:
            print("terminated " + vm)
    else:
        print("Cannot remove all EC2 VMs when 'terminate' set as " +
              str(args.terminate))


terminate_vms(vms)
