#! /usr/bin/env python

'''
This python script launches virtual machine and run a docker container inside the virtual machine.
Author: Chetna Khullar
'''

#All imports
import requests
import time
import subprocess

#User Defined Variables
host_ip = '192.168.1.13'
user = 'demo'
pwd = 'secrete'
project = 'invisible_to_admin'
vm_name='Ubuntu6'

#Method Definitions

#Returns the scoped token and tenant id
def get_tenant(host_ip, user, pwd, project):
    url_keystone = 'http://'+host_ip+':5000/v3/auth/tokens'
    headers = {'Content-Type':'application/json'}
    data = '{"auth":{"identity":{"methods":["password"],"password":{"user":{"name":' \
           '"'+user+'","domain":{"id":"default"},"password":"'+pwd+'"}}},"scope":{"project": ' \
           '{"name":"'+project+'","domain":{"id":"default"}}}}}'
    # Do the HTTP post request
    response = requests.post(url_keystone, data=data, headers=headers)
    # Check for HTTP codes other than 201
    if response.status_code != 201:
        print('Status:', response.content, 'Problem with the request. Exiting.')
        exit()
    else:
        print("Token Generated")
        response_header=response.headers
        token_id=response_header.get('X-Subject-Token')
        response_data = response.json()
        tenant_id=response_data['token']["project"]['id']
        #print("token_id: ",token_id)
        #print("tenant_id",tenant_id)
    return token_id,tenant_id

# Returns the VM(Server) link
def get_server_link(host_ip, token_id, tenant_id,vm_name):
    url ='http://'+host_ip+':8774/v2.1/'+tenant_id+'/servers'
    headers = {'Content-Type':'application/json', 'X-Auth-Token':token_id}
    data=''
    # Do the HTTP get request
    response = requests.get(url, headers=headers, data=data)
    #print(response.text)
    #print(response.status_code)
    server_link=''
    # Check for HTTP codes other than 200
    if response.status_code != 200:
        print('Status:', response.content, 'Problem with the request. Exiting.')
        exit()
    else:

        response_data = response.json()
        server_link=(response_data["servers"]['name'==vm_name]['links'][0]["href"])
        print('Server Found - '+ vm_name)
    return server_link

#To start the server (VM) on devstack
def start_server(server_link,token_id):
    print("Starting Server")
    url =server_link+'/action'
    headers = {'Content-Type':'application/json', 'X-Auth-Token':token_id}
    data='{"os-start": null}'
    response = requests.post(url, headers=headers, data=data)
    # Check for HTTP codes other than 202
    if response.status_code != 202:
        print('Status:', response.content, 'Problem with the request. Exiting.')
        exit()
    else:
        print ("Server Start Accepted")
        #print ("response: ", response.content)
        #server_link=(response_data["servers"]['name'==vm_name]['links'][0]["href"])
    return

#To get the server status
def get_server_status(server_link,token_id):
    url =server_link
    headers = {'Content-Type':'application/json', 'X-Auth-Token':token_id}
    data='{"os-start": null}'
    response = requests.get(url, headers=headers, data=data)
    # Check for HTTP codes other than 200
    if response.status_code != 200:
        print('Status:', response.content, 'Problem with the request. Exiting.')
        exit()
    else:
        #print ("Server Status")
        #print ("response: ", response.text )
        response_data = response.json()
        status=(response_data["server"]['status'])
    return status

#To validate the server status
def validate_server_status(server_link,token_id):
    print("Waiting for server to start")
    time.sleep(10)
    #To get the server status
    server_status = get_server_status(server_link,token_id)
    #Give two more tries in case server is not active
    for i in range(2):
        if (server_status != 'ACTIVE'):
            print("Server not started yet. Retry in progress.")
            time.sleep(10)
            server_status = get_server_status(server_link,token_id)
        else:
            break
    if (server_status == 'ACTIVE'):
        print("Waiting for Services to start on Server")
        time.sleep(10)
        print("Server is Active")

    else:
        print("Server is not started. Check logs for details")
    return server_status

#Start Docker
def start_docker():
    print("Starting Docker")

    subprocess.call("ssh -t ubuntu@172.24.4.5 -i testkey.pem 'docker run -it ubuntu bash'",shell=True)
    return

#To get the scoped token id and tenant id for the user
token_id,tenant_id =get_tenant(host_ip, user, pwd, project)

#To get the server link
server_link = get_server_link(host_ip,token_id,tenant_id,vm_name)

#To get the server status
server_status = get_server_status(server_link,token_id)

#Checks Server Status
if(server_status != 'ACTIVE'):
    start_server(server_link,token_id)
    server_status = validate_server_status(server_link,token_id)
else:
    print("Server is Active")

# Starts docker if the status is Active
if(server_status == 'ACTIVE'):
    start_docker()