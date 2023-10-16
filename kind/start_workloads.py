import utils
from kubernetes import client, config
import random

def get_node_label(node):
    d = {0:"zero", 1:"one", 2:"two", 3:"three", 4:"four", 5:"five"}
    node_id = int(node.split("-")[-1])
    return d[node_id]
    

def partition_nodes(node_list):
    #40% nodes are stateful and 60% are stateless
    def custom_node_sort(s):
        return int(s.split("-")[-1])

    node_list = sorted(node_list, key=custom_node_sort)
    total_nodes = len(node_list)
    stateful_ind = int(total_nodes * 0.4)
    return node_list[:stateful_ind], node_list[stateful_ind:]

OVERLEAF_YAML_PATH = "overleaf/kubernetes"
OVERLEAF_SERVICES = {"mongo":{"stateless":False}, "clsi":{"stateless":True}, "tags":{"stateless":True}, "contacts":{"stateless":True}, "docstore":{"stateless":False}, 
                     "document-updater":{"stateless":True}, "filestore":{"stateless":False}, "notifications":{"stateless":True},
                     "real-time":{"stateless":True}, "redis":{"stateless":False}, "spelling":{"stateless":True}, "track-changes":{"stateless":True}, "web":{"stateless":True}}


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
    print(stateful_nodes)
    print(stateless_nodes)
    for i in range(NUM_OVERLEAF_WORKLOADS):
        # first create namespace
        ns = "overleaf-{}".format(i)
        output = utils.create_namespace(ns)
        if output is None:
            raise Exception("failed to create namespace")
        for service in OVERLEAF_SERVICES.keys():
            # if 'mongo' in service:
            print("Deploying service {}".format(service))
            manifests = utils.fetch_all_files(service)
            # if len(manifests) == 2:
                # implies only deployment and service
                # only node to configure
            service_details = OVERLEAF_SERVICES[service]
            if service_details["stateless"]:
                node = random.choice(stateless_nodes)
            else:
                node = random.choice(stateful_nodes)
            node_label = get_node_label(node)
            print("Placing {} on {}".format(service, node))
            utils.initiate_pod(manifests, service, node_label, ns)
                # elif len(manifests) == 3:
                    # implies pvc, deployment and service
            
    