import os
import requests
from kubernetes import client, config
from kubernetes.client import V1NodeCondition
import time
import utils
from kubernetes.client.rest import ApiException
import subprocess
from typing import Optional, Dict

# def apply_kubernetes_manifest(manifest_file, namespace="overleaf"):
#     # Load the Kubernetes configuration from the default location or provide the path to your kubeconfig file.
#     config.load_kube_config()

#     # Create an instance of the Kubernetes API client.
#     api_instance = client.CoreV1Api()

#     try:
#         # Read the manifest file and apply it.
#         with open(manifest_file) as f:
#             manifest = f.read()

#         # Use kubectl functionality to apply the manifest.
#         response = api_instance.create_namespaced_config_map(
#             namespace,  # Replace with your namespace
#             manifest,
#             pretty="true"
#         )

#         print("Manifest applied successfully.")
#         print(response)
#     except ApiException as e:
#         print("Error applying the manifest: %s" % e)

FIXED=False

def delete_deployment(namespace, deployment_name):
    config.load_kube_config()  # Loads the kubeconfig file or in-cluster config
    api_instance = client.AppsV1Api()

    try:
        api_instance.delete_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=client.V1DeleteOptions(propagation_policy='Foreground')
        )
        print(f"Deployment '{deployment_name}' deleted successfully.")
    except ApiException as e:
        print(f"Error deleting deployment: {e}")

def delete_service(namespace, service_name):
    config.load_kube_config()  # Loads the kubeconfig file or in-cluster config
    api_instance = client.CoreV1Api()

    try:
        api_instance.delete_namespaced_service(
            name=service_name,
            namespace=namespace
        )
        print(f"Service '{service_name}' deleted successfully.")
    except ApiException as e:
        print(f"Error deleting service: {e}")


config.load_kube_config()

# Load the Kubernetes configuration from the default location or a kubeconfig file.
config.load_kube_config()

# Initialize the Kubernetes API client.
v1 = client.CoreV1Api()

@staticmethod
def parse_resource_cpu(resource_str):
    """ Parse CPU string to cpu count. """
    unit_map = {'m': 1e-3, 'K': 1e3}
    value = re.search(r'\d+', resource_str).group()
    unit = resource_str[len(value):]
    return float(value) * unit_map.get(unit, 1)

@staticmethod
def parse_resource_memory(resource_str):
    """ Parse resource string to megabytes. """
    unit_map = {'Ki': 2 ** 10, 'Mi': 2 ** 20, 'Gi': 2 ** 30, 'Ti': 2 ** 40}
    value = re.search(r'\d+', resource_str).group()
    unit = resource_str[len(value):]
    return float(value) * unit_map.get(unit, 1) / (
                2 ** 20)  # Convert to megabytes    
        
def get_cluster_state(kubecoreapi) -> Dict[str, Dict[str, int]]:
    """ Get allocatable resources per node. """
    # Get the nodes and running pods

    limit = None
    continue_token = ""
    nodes, _, _ = kubecoreapi.list_node_with_http_info(limit=limit,
                                                        _continue=continue_token)
    
    pods, _, _ = kubecoreapi.list_pod_for_all_namespaces_with_http_info(
        limit=limit, _continue=continue_token)
    # print(pods)

    nodes = nodes.items
    pods = pods.items
    # print(nodes)
    # print(pods)
    available_resources = {}
    running_pods = set()
    failed_nodes = set()
    for node in nodes:
        for condition in node.status.conditions:
            if condition.type == 'Ready' and condition.status == 'Unknown':
                failed_nodes.add(node.metadata.name)
                
    for node in nodes:
        name = node.metadata.name
        if name in failed_nodes:
            continue
        total_cpu = parse_resource_cpu(node.status.allocatable['cpu'])
        total_memory = parse_resource_memory(
            node.status.allocatable['memory'])
        # total_gpu = int(node.status.allocatable.get('nvidia.com/gpu', 0))

        used_cpu = 0
        used_memory = 0
        # used_gpu = 0

        for pod in pods:
            if pod.spec.node_name == name and pod.status.phase in ['Running', 'Pending']:
                running_pods.add(pod.metadata.name)
                for container in pod.spec.containers:
                    if container.resources.requests:
                        used_cpu += parse_resource_cpu(
                            container.resources.requests.get('cpu', '0m'))
                        used_memory += parse_resource_memory(
                            container.resources.requests.get('memory',
                                                                '0Mi'))
                        # used_gpu += int(container.resources.requests.get(
                        #     'nvidia.com/gpu', 0))

        available_cpu = total_cpu - used_cpu
        available_memory = total_memory - used_memory
        # available_gpu = total_gpu - used_gpu

        available_resources[name] = {
            'cpu': available_cpu,
            'memory': available_memory,
            # 'nvidia.com/gpu': available_gpu
        }
    return available_resources

def list_pods_with_node():
    config.load_kube_config()  # Loads the kubeconfig file or in-cluster config

    v1 = client.CoreV1Api()

    # List all pods in the cluster
    pods = v1.list_pod_for_all_namespaces(watch=False)
    pod_to_node = {}
    node_to_pod = {}
    for pod in pods.items:
        pod_name = pod.metadata.name
        namespace = pod.metadata.namespace
        node_name = pod.spec.node_name
        if namespace == "overleaf":
            pod_to_node[pod_name] = node_name
            if node_name in node_to_pod.keys():
                node_to_pod[node_name].append(pod_name)
            else:
                node_to_pod[node_name] = [pod_name]
    return pod_to_node, node_to_pod
        
        # print(f"Pod: {pod_name} in Namespace: {namespace} is scheduled on Node: {node_name}")

def list_nodes_with_resources():
    # Assumes that metrics server is running
    # check in kube-system whether metrics-server pod is running
    api = client.CustomObjectsApi()
    k8s_nodes = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
    for stats in k8s_nodes['items']:
        print("Node Name: %s\tCPU(in milli cores): %s\tMemory (in MB): %s" % (stats['metadata']['name'], utils.cpu(stats['usage']['cpu']), utils.memory(stats['usage']['memory'])))
    
def delete_microservice(deployment_name, namespace="overleaf"):
    # delete deployments, replicasets, configmaps, pv, pvc, service associated with this
    delete_deployment(namespace, deployment_name)
    delete_service(namespace, deployment_name)

def restart_microservice(deployment_name, namespace="overleaf"):
    kube_manifests = utils.fetch_all_files(deployment_name)
    for manifest in kube_manifests:
        command = "kubectl apply -f {} -n {}".format(manifest, namespace)
        # print(command)
        output = subprocess.check_output(command, shell=True, text=True)
        print(output)
        # apply_kubernetes_manifest(manifest)


def restart_failed_microservice(deployment_name, namespace="overleaf"):
    kube_manifests = utils.fetch_all_files(deployment_name)
    utils.initiate_pod(kube_manifests, deployment_name, "one")
    # print(kube_manifests)
    # for manifest in kube_manifests:
    #     if "pv" in manifest:
    #         cmd = f"kubectl apply -f {manifest}"
    #         output = subprocess.check_output(cmd, shell=True, text=True)
    #         print(output)
    #     elif "deployment" in manifest:
    #         output = utils.initiate_pod(manifest, "one")
    #         print(output)
        # command = "kubectl patch deployment {} --patch '$(cat kind/patch.yml)'".format(dep, namespace)
        # # print(command)
        # output = subprocess.check_output(command, shell=True, text=True)
        # print(output)
        # apply_kubernetes_manifest(manifest)
        
def get_deleted_pod(target_node, node_to_pod, pod_ranks):
    pod_to_node, node_to_pod = list_pods_with_node()
    pods = ["-".join(pod.split("-")[:-2]) for pod in node_to_pod[target_node]]
    return pods

def run_phoenix(failed_nodes, curr_node_to_pod):
    new_pod_to_node, new_node_to_pod = list_pods_with_node()
    # Destroy cluster
    # print("Destroying the cluster")
    deleted_pods = []
    print(NODE_TO_POD)
    print(POD_RANKS)
    node_remaining = utils.get_cluster_state(v1)
    
    for node in failed_nodes:
        p = get_deleted_pod(node, NODE_TO_POD, POD_RANKS)
        [deleted_pods.append(i) for i in p]
        
    print("Deleted pods are the following: ")
    print(deleted_pods)
    # print("Delete them properly")
    # for pod in deleted_pods:
    #     delete_microservice(pod)
    
    # Cordon the failed nodes to prevent from scheduling
    # print("Cordoning off the failed nodes...")
    # for node in failed_nodes:
    #     command = "kubectl cordon {}".format(node)
    # print(command)
    # output = subprocess.check_output(command, shell=True, text=True)
    # print(output)
    # print(delete_pods)
    # delete_pods = ["clsi", "document-updater", "spelling", "web"]
    # for pod in deleted_pods:
    #     delete_microservice(pod)
    # time.sleep(30)
    # Fix cluster
    print("Fixing the cluster...")
    deleted_set = set(deleted_pods)
    already_running = set(POD_RANKS) - deleted_set    
    print("Deleting the following microservices...")  
    for i in range(10, 13):
        if POD_RANKS[i] not in deleted_set:
            delete_microservice(POD_RANKS[i])
    
    print("Restarting the following microservices...")  
    for i in range(0, 10):
        if POD_RANKS[i] not in already_running:
            restart_failed_microservice(POD_RANKS[i])
            # restart_microservice(POD_RANKS[i])
    
    # delete_microservice("web")
    # time.sleep(2)
    # restart_microservice("web")

# Define a function to check node conditions and send alerts if nodes are not ready.
def check_node_conditions_and_alert():
    global FIXED
    nodes = v1.list_node(watch=False)
    failed = False
    failed_nodes = []
    curr_pod_to_node, curr_node_to_pod = list_pods_with_node()
    for node in nodes.items:
        for condition in node.status.conditions:
            if condition.type == 'Ready' and condition.status == 'Unknown':
                print("{} has failed".format(node.metadata.name))
                failed_nodes.append(node.metadata.name)
                failed = True
    if failed and not FIXED:
        run_phoenix(failed_nodes, curr_node_to_pod)
        FIXED = True
    else:
        print("All nodes are healthy")

POD_TO_NODE, NODE_TO_POD = list_pods_with_node()
POD_RANKS = ["mongo", "redis", "docstore", "filestore", "real-time", "document-updater", "web", "clsi", "track-changes","notifications", "contacts", "spelling", "tags"]

if __name__ == "__main__":
    while True:
        # print(NODE_TO_POD)
        print(utils.get_pod_cpu_requests_and_limits(v1))
        print(utils.get_cluster_state(v1))
        check_node_conditions_and_alert()
        time.sleep(15)
