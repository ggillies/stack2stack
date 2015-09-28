#!/usr/bin/env python

from keystoneclient.apiclient import exceptions as api_exceptions
import keystoneclient.openstack.common.apiclient.exceptions
import glanceclient.openstack.common.apiclient.exceptions as glance_exceptions
from keystoneclient.v2_0 import client as keystone_client
from glanceclient import client as glance_client
import glanceclient.exc
from os import path
from os import remove
from neutronclient.v2_0 import client as neutron_client
from novaclient import client as nova_client
import neutronclient.common.exceptions as neutron_exceptions
import random
import string

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
        if i.name in ('admin'):
            continue
        print 'Found tenant with name %s, description is \'%s\'' % (i.name, i.description)
        try:
            new_cloud_keystone_client.tenants.find(name=i.name, description=i.description)
            print 'Tenant %s found, ignoring' % i.name
        except api_exceptions.NotFound:
            print 'Tenant %s not found, adding' % i.name
            if i.name !="alt_demo": # migration of alt_demo tennant throws errors if tempest has been run on new-cloud so skipping it here
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
        if i.name in ('admin', 'alt_demo', 'cinder', 'glance', 'keystone', 'neutron', 'nova', 'heat', 'swift', 'ceilometer'):
            continue
        print 'Found user with name %s, email is %s' % (i.name, i.email)
        try:
            new_cloud_keystone_client.users.find(name=i.name, email=i.email)
            print 'User %s found, ignoring' % i.name
        except api_exceptions.NotFound:
            if i.name !="demo": # migration of demo user throws errors if tempest has been run on new-cloud so skipping it here
                new_password = ''.join(random.choice(string.letters) for i in range(20))
                print 'User %s not found, adding with email: %s and password: %s' % (i.name, i.email, new_password)
                new_cloud_keystone_client.users.create(name=i.name, email=i.email, enabled=i.enabled, password=new_password)

def migrate_roles():
    old_cloud_keystone_client = keystone_client.Client(
                username=old_cloud_username, password=old_cloud_password, tenant_name=old_cloud_project_id,
                auth_url=old_cloud_auth_url, region_name=old_cloud_region_name, insecure=True)

    new_cloud_keystone_client = keystone_client.Client(
                username=new_cloud_username, password=new_cloud_password, tenant_name=new_cloud_project_id,
                auth_url=new_cloud_auth_url, region_name=new_cloud_region_name, insecure=True)

    roles = old_cloud_keystone_client.roles.list()
    for i in roles:
        if i.name in ('heat_stack_user', 'ResellerAdmin', 'SwiftOperator', '_member_', 'admin'):
            continue
        print "found role: %s" % i.name
        try:
            new_cloud_keystone_client.roles.find(name=i.name)
            print "role %s found in target, ignoring" % i.name
        except api_exceptions.NotFound:
            print "role %s not found in target, creating" % i.name
            new_cloud_keystone_client.roles.create(name=i.name)

def migrate_tenant_membership():
    old_cloud_keystone_client = keystone_client.Client(
                username=old_cloud_username, password=old_cloud_password, tenant_name=old_cloud_project_id,
                auth_url=old_cloud_auth_url, region_name=old_cloud_region_name, insecure=True)

    new_cloud_keystone_client = keystone_client.Client(
                username=new_cloud_username, password=new_cloud_password, tenant_name=new_cloud_project_id,
                auth_url=new_cloud_auth_url, region_name=new_cloud_region_name, insecure=True)
    tenants = old_cloud_keystone_client.tenants.list()
    for i in tenants:
        if i.name in ('services', 'service', 'admin'):
            continue
        print 'Found tenant with name %s, members are \'%s\'' % (i.name, i.list_users())
        new_tenant = new_cloud_keystone_client.tenants.find(name=i.name, description=i.description)
        member_role = new_cloud_keystone_client.roles.find(name='_member_')
        for j in i.list_users():
            user = new_cloud_keystone_client.users.find(name=j.name, email=j.email)
            try:
                new_tenant.add_user(user, member_role)
            except api_exceptions.Conflict:
                continue

def migrate_images():
    old_cloud_keystone_client = keystone_client.Client(
                    username=old_cloud_username, password=old_cloud_password, tenant_name=old_cloud_project_id,
                    auth_url=old_cloud_auth_url, region_name=old_cloud_region_name, insecure=True)
    new_cloud_keystone_client = keystone_client.Client(
                username=new_cloud_username, password=new_cloud_password, tenant_name=new_cloud_project_id,
                auth_url=new_cloud_auth_url, region_name=new_cloud_region_name, insecure=True)
    old_endpoint = old_cloud_keystone_client.endpoints.find(service_id=old_cloud_keystone_client.services.find(name='glance').id)
    new_endpoint = new_cloud_keystone_client.endpoints.find(service_id=new_cloud_keystone_client.services.find(name='glance').id)
    old_cloud_glance_client = glance_client.Client('1', token=old_cloud_keystone_client.auth_token, endpoint=old_endpoint.publicurl)
    new_cloud_glance_client = glance_client.Client('1', token=new_cloud_keystone_client.auth_token, endpoint=new_endpoint.publicurl)
    images = old_cloud_glance_client.images.list()
    for i in images:
        print ''
        print 'Old Cloud: Found image           - %s' % i.name
        print '           Image ID              - %s' % i.id
        image_type = 'image'
        if hasattr(i, 'image_type'):
            image_type = i.properties['image_type']
        print '           Image Type            - %s' % image_type
        print '           Image Status          - %s' % i.status
        print '           Image Container       - %s' % i.container_format
        print '           Image Format          - %s' % i.disk_format
        print '           Image Checksum        - %s' % i.checksum
        image_size = (i.size/1024)/1024
        print '           Image Size            - %sMb' % image_size
        print ''
        if not hasattr(i, 'image_type'):
            try:
              new_cloud_glance_client.images.find(name=i.name)
              print 'Info: New Cloud: Image - %s already exists so ignoring' % i.name
              print ''
              print '-------------------------------------------------------------------------------------------'
            except glance_exceptions.NotFound:
                is_public = i.is_public
                if not is_public:
                    old_cloud_glance_client.images.update(i.id, is_public=True)
                if not path.isfile(i.name):
                    print 'New Cloud: image - %s does not yet exist' % i.name
                    print ''
                    print 'Local Filesytem: Downloading temp image to local disk'
                    print '                 Preparing to transfer %s to New Cloud' % i.name
                    print ''
                    try:
                        with open(i.name, 'wb') as f:
                            for chunk in old_cloud_glance_client.images.data(i.id):
                                f.write(chunk)
                        f.close()
                    except glanceclient.exc.HTTPInternalServerError:
                        print ''
                        print 'Error: There was a problem uploading this Image - %s - ID: %s - This was caused by an HTTPInternalServerError at this time. You may want to investigate further' % (i.name, i.id)
                        print ''
                        continue
                if not is_public:
                    old_cloud_glance_client.images.update(i.id, is_public=False)

                new_owner_id = new_cloud_keystone_client.tenants.find(name=old_cloud_keystone_client.tenants.find(id=i.owner).name, description=old_cloud_keystone_client.tenants.find(id=i.owner).description).id
                try:
                    j = new_cloud_glance_client.images.create(id=i.id, name=i.name, is_public=is_public, disk_format = i.disk_format, container_format = i.container_format, owner = new_owner_id)
                    except:
                    print 'Error: Image - %s -ID: %s - conflicts with existing ID. You may want to investigate further' % (i.name, i.id)
                    print 'Error: This ID conflict usually means that the ID previously existed on the new cloud and has been deleted.'
                    print 'Info: You may need to remove from the mysql glance:'
                    print 'Info: You can try the following:'
                    print 'Info: mysql glance'
                    print "Info: delete from image_locations where image_id='%s';" % i.id
                    print "Info: delete from image_properties where image_id='%s';" % i.id
                    print "Info: delete from images where id='%s';" % i.id
                    continue
                print 'New Cloud: Creating and uploading image - %s' % j.name
                print ''
                j.update(data=open(j.name, 'rb'))
                print 'Local Filesytem: Removing temp image - %s' % i.name
                print ''
                print '============================= Transfer and cleanup complete ==============================='
                print ''
                remove(i.name)

def migrate_networks_nova_network_to_neutron():
    old_cloud_keystone_client = keystone_client.Client(
                    username=old_cloud_username, password=old_cloud_password, tenant_name=old_cloud_project_id,
                    auth_url=old_cloud_auth_url, region_name=old_cloud_region_name, insecure=True)
    new_cloud_keystone_client = keystone_client.Client(
                username=new_cloud_username, password=new_cloud_password, tenant_name=new_cloud_project_id,
                auth_url=new_cloud_auth_url, region_name=new_cloud_region_name, insecure=True)
    old_cloud_nova_client = nova_client.Client(2, old_cloud_username, old_cloud_password, old_cloud_project_id, old_cloud_auth_url)
    new_cloud_neutron_client = neutron_client.Client(username=new_cloud_username, password=new_cloud_password,
                          tenant_name=new_cloud_project_id, auth_url=new_cloud_auth_url)

    networks = old_cloud_nova_client.networks.list()
    for i in networks:
        try:
            old_cloud_tenant = old_cloud_keystone_client.tenants.find(id=i.project_id)
        except api_exceptions.NotFound:
            print 'Bad or missing tenant in old cloud %s, skipping this orphaned network' % i.project_id
            continue
        print 'Found network %s owned by %s' % (i.label, old_cloud_tenant.name)
        try:
            new_cloud_tenant = new_cloud_keystone_client.tenants.find(name=old_cloud_tenant.name, description=old_cloud_tenant.description)
        except api_exceptions.NotFound:
            print 'Tenant %s not found in new cloud, confirm tenant migration was done correctly' % old_cloud_tenant.name
            continue
        new_cloud_networks = new_cloud_neutron_client.list_networks(name=i.label, tenant_id=new_cloud_tenant.id)
        if len(new_cloud_networks['networks']) == 0:
            print('Creating network %s in tenant %s' % (i.label, new_cloud_tenant.name))
            new_cloud_network = new_cloud_neutron_client.create_network({'network':{'name':i.label, 'tenant_id':new_cloud_tenant.id}})
            new_cloud_subnet = new_cloud_neutron_client.create_subnet({'subnet':{'name':i.label, 'network_id':new_cloud_network['network']['id'],
                                'tenant_id':new_cloud_tenant.id,'ip_version':4, 'cidr':i.cidr, 'enable_dhcp':True}})
        else:
            print('Network %s already exists in new cloud, ignoring' % i.label)

def main():
    migrate_tenants()
    migrate_users()
    migrate_roles()
    migrate_tenant_membership()
    migrate_images()
    migrate_networks_nova_network_to_neutron()

if __name__ == "__main__":
    main()
