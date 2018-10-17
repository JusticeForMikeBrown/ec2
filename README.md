EC2 VMs
===============

`create_vm.py` will deploy EC2 VM with SSH Security Group writing Public DNS entries to a file

`terminate_vm.py` will remove all EC2 VMs.

Requirements
------------

You must be using Python 2.7 with key auth already configured


[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)


[awscli](https://pypi.org/project/awscli)


[joblib](https://pypi.org/project/joblib/)


Usage
--------------

`create_vm.py`

Here's how to use the script:
 
    python create_vm.py number type os

Where:

    number = number of vms
    type   = type of ec2 instance
    os     = operating system
    

`terminate_vm.py`

    python terminate_vm.py
    
Where:

    terminate = positional argument that must be True - default = False

TODO
------------
Get type and os dynamically

Perhaps add integration with [Ansible EC2 Dynamic Inventory](https://raw.github.com/ansible/ansible/devel/contrib/inventory/ec2.py)
