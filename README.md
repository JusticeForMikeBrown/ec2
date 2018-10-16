EC2 VMs
===============

Basic script to deploy EC2 VM with SSH Security Group writing Public DNS entries to a file


Requirements
------------

You must be using Python 2.7 with key auth already configured


[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)


[awscli](https://pypi.org/project/awscli)


Usage
--------------

Here's how to use the script:
 
    python create_vm.py number type os

Where:

    number = number of vms
    type   = type of ec2 instance
    os     = operating system

TODO
------------
Get type and os dynamically
