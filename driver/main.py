import setup_cloudlab
import re

STARTUP = "kind/node-0_startup.sh"

def get_ip(host):
    cmd = "hostname -I | awk '{print $1}'"
    output = setup_cloudlab.run_remote_cmd_output(host, cmd)
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ip_addresses = re.findall(ip_pattern, output)
    return ip_addresses[0]
    
    
    
def label_nodes(node_info_dict):
    s = """#!/bin/bash
# install python 3.9
sudo add-apt-repository ppa:deadsnakes/ppa; sudo apt update; sudo apt -y install python3.9; sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 2; sudo apt-get -y install python3-pip
# install kubernetes package
sudo apt-get -y install python3.9-distutils; python3 -m pip install kubernetes; python3 -m pip install networkx; python3 -m pip install numpy; python3 -m pip install requests; python3 -m pip install sortedcontainers
"""
    for node in node_info_dict.keys():
        node_id = node.split("-")[-1].strip()
        s += "kubectl label node {} nodes={}\n".format(node, node_id)
    return s

if __name__ == "__main__":
    list_view_str = """node-5	pc492	d710	Emulab	ready	Finished	emulab-ops/UBUNTU22-64-STD	ssh kapila1@pc492.emulab.net 		
 
node-4	pc477	d710	Emulab	ready	Finished	emulab-ops/UBUNTU22-64-STD	ssh kapila1@pc477.emulab.net 		
 
node-7	pc474	d710	Emulab	ready	Finished	emulab-ops/UBUNTU22-64-STD	ssh kapila1@pc474.emulab.net 		
 
node-6	pc479	d710	Emulab	ready	Finished	emulab-ops/UBUNTU22-64-STD	ssh kapila1@pc479.emulab.net 		
 
node-1	pc476	d710	Emulab	ready	Finished	emulab-ops/UBUNTU22-64-STD	ssh kapila1@pc476.emulab.net 		
 
node-0	pc499	d710	Emulab	ready	Finished	emulab-ops/UBUNTU22-64-STD	ssh kapila1@pc499.emulab.net 		
 
node-3	pc498	d710	Emulab	ready	Finished	emulab-ops/UBUNTU22-64-STD	ssh kapila1@pc498.emulab.net 		
 
node-2	pc473	d710	Emulab	ready	Finished	emulab-ops/UBUNTU22-64-STD	ssh kapila1@pc473.emulab.net 		
 
node-9	pc491	d710	Emulab	ready	Finished	emulab-ops/UBUNTU22-64-STD	ssh kapila1@pc491.emulab.net 		
 
node-8	pc478	d710	Emulab	ready	Finished	emulab-ops/UBUNTU22-64-STD	ssh kapila1@pc478.emulab.net 		

"""
    node_info_dict = setup_cloudlab.get_node_info_dict(list_view_str)
    print(node_info_dict)
    s = label_nodes(node_info_dict)
    # label worker nodes -- all nodes excluding node-0
    with open(STARTUP, "w") as file:
        file.write(s)
    file.close()
    # # now copy STARTUP file into node-0 and then execute it
    setup_cloudlab.send_dir(node_info_dict['node-0']['host'], "kind")  
    setup_cloudlab.send_dir(node_info_dict['node-0']['host'], "overleaf")
    setup_cloudlab.send_dir(node_info_dict['node-0']['host'], "kind/RMScheduler")
    # # get ip of cloudlab cluster 
    ip = get_ip(node_info_dict['node-0']['host'])
    # print("The IP address for the cluster is {}".format(ip))
    # num_workloads = 2
    # for i in num_workloads:
        
        
    