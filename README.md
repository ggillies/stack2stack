Stack2Stack
===========

stack2stack is a simple python script to aid data migration from one Openstack
cloud to another through use of the APIs. It aims to cleanly migrate the data
keeping as much in sync as possible, up to the limitations of the Openstack
APIs themselves. Currently the script migrates

* Keystone Users
* Keystone Tenants
* Keystone roles
* Keystone Tenant Memberships
* Glance Images
* Networks from nova networking to neutron
* Security groups from nova networking to neutron

How to use
==========

Simply edit the top of the stack2stack.py file, defining the credentials of the
two openstack clouds you wish to use in the migration (old_cloud_* are the
source cloud, new_cloud_* are the target cloud). Then simply run

````
python -u stack2stack.py | tee stack2stack.log
````

This will run the migration and capture the output to stdout and the log file
stack2stack.log

Limitations
===========

Currently stack2stack has the following limitations, some of which are slowly being addressed

* As the api offers no way to expose the underlying cinder volumes, cinder
  volumes are not migrated
* As the APIs do not expose users passwords, currently each user account
  in the new cloud has their password reset (and is printed in the log)
* No support for migration neutron-to-neutron networks (yet)
