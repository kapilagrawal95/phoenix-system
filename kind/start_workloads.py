import utils
from kubernetes import client, config
import random
import copy
import create_users
import Phoenix
import subprocess
import time

def get_node_label(node):
    # d = {0:"zero", 1:"one", 2:"two", 3:"three", 4:"four", 5:"five"}
    node_id = int(node.split("-")[-1])
    return node_id

def partition_nodes(node_list):
    #40% nodes are stateful and 60% are stateless
    def custom_node_sort(s):
        return int(s.split("-")[-1])

    node_list = sorted(node_list, key=custom_node_sort)
    total_nodes = len(node_list)
    stateful_ind = int(total_nodes * 0.4)
    return node_list[:stateful_ind], node_list[stateful_ind:]

OVERLEAF_YAML_PATH = "overleaf/kubernetes"
OVERLEAF_SERVICES = {"mongo":{"stateless":False, "env_vars":{"MONGO_CPU": None}}, 
                     "clsi":{"stateless":True, "env_vars":{"CLSI_CPU": None}}, 
                     "tags":{"stateless":True, "env_vars":{"TAGS_CPU": None}}, 
                     "contacts":{"stateless":True, "env_vars":{"CONTACTS_CPU": None}}, 
                     "docstore":{"stateless":False, "env_vars":{"DOCSTORE_CPU": None}}, 
                     "document-updater":{"stateless":True, "env_vars":{"DOCUMENT_UPDATER_CPU": None}}, 
                     "filestore":{"stateless":False, "env_vars":{"FILESTORE_CPU": None}}, 
                     "notifications":{"stateless":True, "env_vars":{"NOTIFICATIONS_CPU": None}},
                     "real-time":{"stateless":True, "env_vars":{"REAL_TIME_NODEPORT":None, "REAL_TIME_CPU":None}}, 
                     "redis":{"stateless":False, "env_vars":{"REDIS_CPU": None}}, 
                     "spelling":{"stateless":True, "env_vars":{"SPELLING_CPU": None}}, 
                     "track-changes":{"stateless":True, "env_vars":{"TRACK_CHANGES_CPU": None}}, 
                     "web":{"stateless":True, "env_vars":{"WEB_NODEPORT":None, "SHARELATEX_REAL_TIME_URL_VALUE":None, "WEB_CPU": None}}}
OVERLEAF_PORTS = ["WEB_NODEPORT", "REAL_TIME_NODEPORT"]
ALREADY_ASSIGNED_PORTS = set()
BASE_PORT = 30910
COUNTER = 0

def assign_ports():
    global BASE_PORT
    global COUNTER
    port =  BASE_PORT + COUNTER
    COUNTER += 1
    return port
    # assignments = {}
    # for port in OVERLEAF_PORTS:
    #     assigned_port_num = BASE_PORT+COUNTER
    #     assignments[port] = assigned_port_num
    #     COUNTER += 1
    #     ALREADY_ASSIGNED_PORTS.add(assigned_port_num)
    # return assignments
    
def get_cpu(service):
    CPU_LOOKUP = {"web": "4000m",
                  "clsi": "3000m",
                  "track-changes": "3000m",
                  "real-time": "3000m",
                  "mongo": "2000m",
                  "redis": "1000m",
                  "spelling": "500m",
                  "tags":"300m",
                  "contacts": "200m",
                  "docstore": "500m",
                  "filestore": "1000m",
                  "notifications": "500m",
                  "document-updater": "3000m",
                  "chat": "1000m"
                  }
    return CPU_LOOKUP[service]
    
def assign_env_variables(service, env_vars, context):
    vars = {}
    for var in env_vars:
        if "PORT" in var:
            port_num = assign_ports()
            vars[var] = port_num
        elif "REAL_TIME_URL" in var:
            ip = utils.get_ip()
            real_time_port = context["real-time"]["env_vars"]["REAL_TIME_NODEPORT"]
            val = ip+":"+str(real_time_port)
            vars[var] = val
        elif "CPU" in var:
            cpu = get_cpu(service)
            vars[var] = cpu
    return vars
    
if __name__ == "__main__":
    NUM_OVERLEAF_WORKLOADS=1
    # Load the Kubernetes configuration from the default location or a kubeconfig file.
    config.load_kube_config()
    # Initialize the Kubernetes API client.
    v1 = client.CoreV1Api()
    cluster_state = utils.get_cluster_state(v1)
    nodes = list(cluster_state.keys())
    stateful_nodes, stateless_nodes = partition_nodes(nodes)
    stateful_nodes = stateful_nodes[1:]
    stateless_nodes = stateless_nodes[:-1]
    print(stateful_nodes)
    print(stateless_nodes)
    # workloads = {}
    # for i in range(NUM_OVERLEAF_WORKLOADS):
    #     ns = "overleaf-{}".format(i)
    #     print("Creating namespace {}...".format(ns))
    #     output = utils.create_namespace(ns)
    #     if output is None:
    #         raise Exception("failed to create namespace")
    #     # tag namespaces
    #     cmd = "kubectl label ns {} phoenix=enabled".format(ns)
    #     output = subprocess.check_output(cmd, shell=True, text=True)
    #     print(output)
    #     overleaf_instance = copy.deepcopy(OVERLEAF_SERVICES)
    #     for service in overleaf_instance.keys():
    #         print("Deploying service {}".format(service))
    #         # assign environment variables, if any
    #         service_details = overleaf_instance[service]
    #         if len(service_details["env_vars"]):
    #             all_vars = list(service_details["env_vars"].keys())
    #             env_vars = assign_env_variables(service, all_vars, overleaf_instance)
    #             service_details["env_vars"] = dict(env_vars)
    #         cpu = int(next((value for key, value in service_details["env_vars"].items() if "_CPU" in key), None).replace("m", ""))/1000
    #         print("CPU requirement for {} is {}".format(service, cpu))
    #         if service_details["stateless"]:
    #             # node = random.choice(stateless_nodes) # earlier was using random
    #             node = utils.most_empty_bin_packing(v1,cpu, stateless_nodes)
    #         else:
    #             # node = random.choice(stateful_nodes)
    #             node = utils.most_empty_bin_packing(v1,cpu, stateful_nodes)
    #         node_label = get_node_label(node)
    #         print("Trying to place {} on {} using most_empty bin packing policy".format(service, node_label))
    #         print("Fetching manifest files...")
    #         manifests = utils.fetch_all_files(service, ROOT="kubernetes/")
    #         print("Found {} manifests".format(len(manifests)))
    #         utils.initiate_pod(manifests, service, str(node_label), ns, env_vars=service_details["env_vars"])
    #     workloads[ns] = overleaf_instance
    
    # print(workloads)
    # Check if all pods are running in all valid namespaces
    flag=True
    config.load_kube_config()
    # List all namespaces with label "phoenix=enabled"
    v1 = client.CoreV1Api()
    # while flag:
    #     namespaces = v1.list_namespace(label_selector="phoenix=enabled")
    #     flags = []
    #     for ns in namespaces.items:
    #         namespace_name = ns.metadata.name
    #         if utils.check_pods_in_namespace(namespace_name, v1):
    #             print(f'All pods are running in namespace "{namespace_name}"')
    #             flags.append(False)
    #         else:
    #             print(f'Not all pods are running in namespace "{namespace_name}"')
    #             flags.append(True)
    #     flag = any(flags)
    #     time.sleep(10)
    
    # once all pods are running create_users
    # for namespace in workloads.keys():
    #     create_users.create_overleaf_users(10, namespace, workloads[namespace]["web"]["env_vars"]["WEB_NODEPORT"])
    workloads = {'overleaf-0': {'mongo': {'stateless': False, 'env_vars': {'MONGO_CPU': '2000m'}}, 'clsi': {'stateless': True, 'env_vars': {'CLSI_CPU': '3000m'}}, 'tags': {'stateless': True, 'env_vars': {'TAGS_CPU': '300m'}}, 'contacts': {'stateless': True, 'env_vars': {'CONTACTS_CPU': '200m'}}, 'docstore': {'stateless': False, 'env_vars': {'DOCSTORE_CPU': '500m'}}, 'document-updater': {'stateless': True, 'env_vars': {'DOCUMENT_UPDATER_CPU': '3000m'}}, 'filestore': {'stateless': False, 'env_vars': {'FILESTORE_CPU': '1000m'}}, 'notifications': {'stateless': True, 'env_vars': {'NOTIFICATIONS_CPU': '500m'}}, 'real-time': {'stateless': True, 'env_vars': {'REAL_TIME_NODEPORT': 30910, 'REAL_TIME_CPU': '3000m'}}, 'redis': {'stateless': False, 'env_vars': {'REDIS_CPU': '1000m'}}, 'spelling': {'stateless': True, 'env_vars': {'SPELLING_CPU': '500m'}}, 'track-changes': {'stateless': True, 'env_vars': {'TRACK_CHANGES_CPU': '3000m'}}, 'web': {'stateless': False, 'env_vars': {'WEB_NODEPORT': 30911, 'SHARELATEX_REAL_TIME_URL_VALUE': '155.98.38.116:30910', 'WEB_CPU': '5000m'}}}}
    # Now start phoenix
    Phoenix.phoenix(v1, workloads)
    