#!/usr/bin/env python

from keystoneclient.apiclient import exceptions as api_exceptions
import keystoneclient.openstack.common.apiclient.exceptions
from keystoneclient.v2_0 import client as keystone_client
import neutronclient.common.exceptions

old_cloud_username='admin'
old_cloud_password='admin'
old_cloud_project_id='admin'
old_cloud_auth_url='http://127.0.0.1:5000/v2.0'
old_cloud_region_name='regionOne'

new_cloud_username='admin'
new_cloud_password='admin'
new_cloud_project_id='admin'
new_cloud_auth_url='http://127.0.0.1:5000/v2.0'
new_cloud_region_name='regionOne'

def migrate_tenants():
    old_cloud_keystone_client = keystone_client.Client(
                username=old_cloud_username, password=old_cloud_password, tenant_name=old_cloud_project_id,
                auth_url=old_cloud_auth_url, region_name=old_cloud_region_name, insecure=True)

    new_cloud_keystone_client = keystone_client.Client(
                username=new_cloud_username, password=new_cloud_password, tenant_name=new_cloud_project_id,
                auth_url=new_cloud_auth_url, region_name=new_cloud_region_name, insecure=True)
    tenants = old_cloud_keystone_client.tenants.list()
    for i in tenants:
        print 'Found tenant with name %s, description is \'%s\'' % (i.name, i.description)
        try:
            new_cloud_keystone_client.tenants.find(name=i.name, description=i.description)
            print 'Tenant %s found, ignoring' % i.name
        except api_exceptions.NotFound:
            print 'Tenant %s not found, adding' % i.name
            new_cloud_keystone_client.tenants.create(tenant_name=i.name, description=i.description, enabled=i.enabled)

def migrate_users():
    old_cloud_keystone_client = keystone_client.Client(
                username=old_cloud_username, password=old_cloud_password, tenant_name=old_cloud_project_id,
                auth_url=old_cloud_auth_url, region_name=old_cloud_region_name, insecure=True)

    new_cloud_keystone_client = keystone_client.Client(
                username=new_cloud_username, password=new_cloud_password, tenant_name=new_cloud_project_id,
                auth_url=new_cloud_auth_url, region_name=new_cloud_region_name, insecure=True)

    users = old_cloud_keystone_client.users.list()
    for i in users:
        print 'Found user with name %s, email is %s' % (i.name, i.email)
        try:
            new_cloud_keystone_client.users.find(name=i.name, email=i.email)
            print 'User %s found, ignoring' % i.name
        except api_exceptions.NotFound:
            print 'User %s not found, adding' % i.name
            new_cloud_keystone_client.users.create(name=i.name, email=i.email, enabled=i.enabled)

def main():
    migrate_tenants()
    migrate_users()

if __name__ == "__main__":
    main()
