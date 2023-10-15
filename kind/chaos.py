import subprocess
import utils

NODES_TO_DEL = ["2"]

def stop_kubelet(node):
    try:
        # if a kind cluster then
        cmd = f"docker exec -it {node} /bin/bash -c 'systemctl stop kubelet'" # else replace docker exec kubectl exec
        subprocess.check_call(cmd, shell=True)
        print(f"Stopped kubelet on {node} successfully")
    except:
        print(f"Error stopping kubelet on {node}: {e}")
    
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

def get_all_pods_to_delete(pod_to_node):
    result_dict = {}

    # Iterate through the items in the original dictionary
    for key, value in pod_to_node.items():
        # If the value is not already in the result dictionary, create a new entry
        if value not in result_dict:
            result_dict[value] = key
        # If the value is already in the result dictionary, append the key to a list
        else:
            if isinstance(result_dict[value], list):
                result_dict[value].append(key)
            else:
                result_dict[value] = [result_dict[value], key]
    
    list_of_nodes = list(result_dict.keys())
    list_of_pods_to_kill = []
    list_of_nodes_to_kill = []
    for ele in NODES_TO_DEL:
        for node in list_of_nodes:
            if ele in node:
                list_of_nodes_to_kill.append(node)
                pods = result_dict[node]
                [list_of_pods_to_kill.append(pod) for pod in pods]
    return list_of_pods_to_kill, list_of_nodes_to_kill
    
def parse_pod_name(pod):
    return "-".join(pod.split("-")[:-2])
    
            
def get_all_objects_associated(pod):
    deployment = parse_pod_name(pod)
    files = utils.fetch_all_files(deployment)
    objects = {"pod":pod, "deployment":deployment}
    for f in files:
        if 'pv' in f:
            objects["pvc"] = utils.get_resource_name_from_yaml(f)
    return objects
    
def run_chaos(pods, nodes):
    processes = []
    for pod in pods:
        deployment = parse_pod_name(pod)
        objects = get_all_objects_associated(pod)
        delete_pod_forcefully(objects["pod"])
        delete_deployment_forcefully(objects["deployment"])
        # if "pvc" in objects:
        #     processes.append(delete_pvc_forcefully_async(objects["pvc"]))
    for node in nodes:
        stop_kubelet(node)
    

if __name__ == "__main__":
    pod_to_node = get_pods_current_allocation()
    print(pod_to_node)    
    pods, nodes = get_all_pods_to_delete(pod_to_node)
    print(pods, nodes)
    run_chaos(pods, nodes)