import subprocess
import utils
from kubernetes import client, config
import logging
import datetime

NODES_TO_DEL = ["5", "7"]

NODE_INFO_DICT = {'node-5': {'startup': 'Finished', 'host': 'kapila1@pc492.emulab.net'}, 'node-4': {'startup': 'Finished', 'host': 'kapila1@pc477.emulab.net'}, 'node-7': {'startup': 'Finished', 'host': 'kapila1@pc474.emulab.net'}, 'node-6': {'startup': 'Finished', 'host': 'kapila1@pc479.emulab.net'}, 'node-1': {'startup': 'Finished', 'host': 'kapila1@pc476.emulab.net'}, 'node-0': {'startup': 'Finished', 'host': 'kapila1@pc499.emulab.net'}, 'node-3': {'startup': 'Finished', 'host': 'kapila1@pc498.emulab.net'}, 'node-2': {'startup': 'Finished', 'host': 'kapila1@pc473.emulab.net'}, 'node-9': {'startup': 'Finished', 'host': 'kapila1@pc491.emulab.net'}, 'node-8': {'startup': 'Finished', 'host': 'kapila1@pc478.emulab.net'}}

def run_remote_cmd_output(host, cmd):
    output = subprocess.check_output(f"ssh -p 22 -o StrictHostKeyChecking=no {host} -t {cmd}", shell=True, text=True)
    return output

def start_kubelet(node):
    host = NODE_INFO_DICT[node]['host']
    cmd = "sudo systemctl start kubelet"
    run_remote_cmd_output(host, cmd)
    
def stop_kubelet(node):
    host = NODE_INFO_DICT[node]['host']
    cmd = "sudo systemctl stop kubelet"
    run_remote_cmd_output(host, cmd)
    # print(host, cmd)
    
def stop_kubelet_docker(node):
    try:
        # if a kind cluster then
        cmd = f"docker exec -it {node} /bin/bash -c 'systemctl stop kubelet'" # else replace docker exec kubectl exec
        subprocess.check_call(cmd, shell=True)
        print(f"Stopped kubelet on {node} successfully")
    except:
        print(f"Error stopping kubelet on {node}")
    
def delete_deployment_forcefully(deployment, namespace="overleaf"):
    try:
        # Use the kubectl command to delete the pod forcefully
        cmd = f"kubectl delete deployment {deployment} --namespace {namespace} --grace-period=0 --force"
        subprocess.check_call(cmd, shell=True)
        print(f"Deleted deployment {deployment} forcefully.")
    except subprocess.CalledProcessError as e:
        print(f"Error deleting deployment {deployment}: {e}")
        
def delete_pod_forcefully(pod_name, namespace="overleaf"):
    try:
        # Use the kubectl command to delete the pod forcefully
        cmd = f"kubectl delete pod {pod_name} --namespace {namespace} --grace-period=0 --force"
        subprocess.check_call(cmd, shell=True)
        print(f"Deleted pod {pod_name} forcefully.")
    except subprocess.CalledProcessError as e:
        print(f"Error deleting pod {pod_name}: {e}")


def delete_pvc_forcefully_async(pvc, namespace="overleaf"):
    process = None
    try:
        # Use the kubectl command to delete the pod forcefully
        cmd = f"kubectl delete pvc {pvc} --namespace {namespace} --now"
        subprocess.Popen(cmd, shell=True)
        # subprocess.check_call(cmd, shell=True)
        print(f"Deleting pvc {pvc} async.")
    except subprocess.CalledProcessError as e:
        print(f"Error deleting pvc {pvc}: {e}")
    return process
        
def get_pods_current_allocation(namespace="overleaf"):
    cmd = f"kubectl get pods -o custom-columns=POD:.metadata.name,NODE:.spec.nodeName -n {namespace} --no-headers | tr -s ' ' '|'"
    output = subprocess.check_output(cmd, shell=True)
    output = output.decode("utf-8").strip()
    pod_to_node = {}
    lines = output.split('\n')
    # Iterate through each line
    for line in lines:
        # Split each line into key and value using the pipe character as a separator
        parts = line.split('|')
        # Ensure there are two parts (key and value)
        if len(parts) == 2:
            key, value = parts[0], parts[1]
            
            # Store key-value pairs in the dictionary
            pod_to_node[key] = value
    return pod_to_node

def get_all_pods_to_delete(node_to_pod):
    list_of_nodes = list(node_to_pod.keys())
    list_of_pods_to_kill = []
    list_of_nodes_to_kill = []
    for ele in NODES_TO_DEL:
        for node in list_of_nodes:
            if ele in node:
                list_of_nodes_to_kill.append(node)
                pods = node_to_pod[node]
                [list_of_pods_to_kill.append(utils.parse_pod_name(pod)) for pod in pods]
    return list_of_pods_to_kill, list_of_nodes_to_kill
    
def parse_pod_name(pod):
    return "-".join(pod.split("-")[:-2])
    
            
def get_all_objects_associated(deployment, ns):
    files = utils.fetch_all_files(deployment, ROOT="kubernetes/")
    pod_command = "kubectl get pods -n {} | grep '^{}' | awk {}".format(ns, deployment, "'{print $1}'")
    output = subprocess.check_output(pod_command, shell=True)
    pod_name = output.decode("utf-8").strip()
    objects = {"pod":pod_name, "deployment":deployment}
    # for f in files:
    #     if 'pv' in f:
    #         objects["pvc"] = utils.get_resource_name_from_yaml(f)
    return objects
    
def run_chaos(pods, nodes, logger, host_name):
    processes = []
    for pod in pods:
        ns_name, ms_name = pod
        objects = get_all_objects_associated(ms_name, ns_name)
        delete_pod_forcefully(objects["pod"], namespace=ns_name)
        delete_deployment_forcefully(objects["deployment"], namespace=ns_name)
        logger.info("[{}] {} [Chaos] Forcefully deleted deployment {} on namespace {}.".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), host_name, ms_name, ns_name))
    #     # if "pvc" in objects:
    #     #     processes.append(delete_pvc_forcefully_async(objects["pvc"]))
    for node in nodes:
        stop_kubelet(node)
        logger.info("[{}] {} [Chaos] Stopped Kubelet on node {}.".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), host_name, node))
    
if __name__ == "__main__":
    logging.basicConfig(filename='logs/chaos.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    name_of_host_cmd = "hostname"
    host_name = str(subprocess.check_output(name_of_host_cmd, shell=True, text=True)).strip()
    config.load_kube_config()
    #Initialize the Kubernetes API client.
    v1 = client.CoreV1Api()
    pod_to_node, node_to_pod = utils.list_pods_with_node(v1, phoenix_enabled=True)
    print(node_to_pod)
    # print(pod_to_node, node_to_pod)    
    pods, nodes = get_all_pods_to_delete(node_to_pod)
    print(pods, nodes)
    logger.info("[{}] {} [Chaos] Beginning chaos experiment on nodes {}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), host_name, nodes))
    run_chaos(pods, nodes, logger, host_name)
    
    ## Only during testing..
    # for node in nodes:
    #     start_kubelet(node)
