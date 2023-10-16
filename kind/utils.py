import re
from pathlib import Path
import yaml

import subprocess
import os

import json
import logging
import re
import threading
import time
from collections import deque
from typing import Optional, Dict

from kubernetes.client import V1Pod
from kubernetes import client, config, watch

def get_pod_cpu_requests_and_limits(api):
    # Load Kubernetes configuration from the default location
    # config.load_kube_config()

    # Create a Kubernetes API client
    # api = client.CoreV1Api()

    # Get the list of pods in the cluster
    pods = api.list_pod_for_all_namespaces().items

    pod_resources = []

    for pod in pods:
        pod_name = pod.metadata.name
        
        namespace = pod.metadata.namespace
        if namespace != "overleaf":
          continue
        print(pod_name)
        # Get the pod's resource requests and limits
        cpu_request = pod.spec.containers[0].resources.requests.get('cpu', 'N/A')
        cpu_limit = pod.spec.containers[0].resources.limits.get('cpu', 'N/A')

        pod_resources.append({
            "Pod Name": pod_name,
            "Namespace": namespace,
            "CPU Request": cpu_request,
            "CPU Limit": cpu_limit
        })

    return pod_resources
  
# @staticmethod
def parse_resource_cpu(resource_str):
    """ Parse CPU string to cpu count. """
    unit_map = {'m': 1e-3, 'K': 1e3}
    value = re.search(r'\d+', resource_str).group()
    unit = resource_str[len(value):]
    return float(value) * unit_map.get(unit, 1)

# @staticmethod
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

def create_namespace(ns):
    cmd = "kubectl create namespace {}".format(ns)
    try:
      output = subprocess.check_output(cmd, shell=True)
      print("Successfully created namespace {}".format(ns))
    except:
      print("Failed to create namespace {}".format(ns))
      output = None
    return output
  
def initiate_pod(manifest_files, deployment_name, node_name, namespace):
    # cmd = f"kubectl apply -f overleaf/kubernetes/contacts-pv.yaml"
    # subprocess.check_call(cmd, shell=True)
    # Set the environment variable
    pv_claim_var = str(deployment_name.upper() + "_CLAIMNAME").replace("-", "_")
    node_var = str(deployment_name.upper() + "_NODE").replace("-", "_")
    for file in manifest_files:
      if "pv" in file:
        pvc_cmd = "kubectl get pvc -n {} | grep '^{}' | awk '{}'".format(namespace, deployment_name, "{print $1}")
        output = subprocess.check_output(pvc_cmd, shell=True)
        output = output.decode("utf-8").strip()
        for i in range(0, 9):
          pvc_name = "{}-claim{}".format(deployment_name, i)
          if pvc_name not in output:
            break
        os.environ[pv_claim_var] = pvc_name
        print("Setting {} variable to {}".format(pv_claim_var, pvc_name))
        envsubst_command = ["envsubst < {} | kubectl apply -n {} -f -".format(file, namespace)]
        output = subprocess.check_output(envsubst_command, shell=True, text=True)
        print(output)
      elif "deployment" in file:
        # os.environ[pv_claim_var] = pvc_name
        os.environ[node_var] = str(node_name)
        print("Setting {} variable to {}".format(node_var, node_name))
        envsubst_command = ["envsubst < {} | kubectl apply -n {} -f -".format(file, namespace)]
        output = subprocess.check_output(envsubst_command, shell=True, text=True)
      print(output)
    # envsubst_command = ["envsubst < {} | kubectl apply -f -".format(manifest_file)]
    # os.environ["CONTACTS_NODE"] = str(node_name)
    # manifest_file = "overleaf/kubernetes/contacts-deployment.yaml"
    # envsubst_command = ["envsubst < {} | kubectl apply -f -".format(manifest_file)]
    # output = subprocess.check_output(envsubst_command, shell=True, text=True)
    # return output
  

def get_resource_name_from_yaml(yaml_file_path):
    try:
        with open(yaml_file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
            if 'metadata' in yaml_data and 'name' in yaml_data['metadata']:
                return yaml_data['metadata']['name']
            else:
                return None
    except Exception as e:
        print(f"Error reading or parsing the YAML file: {str(e)}")
        return None

def custom_sort(s):
    order = {"pv": 0, "pvc": 1, "deployment": 2, "service": 3}
    # s = str(s).replace(".yaml", "")
    # return 1
    return (order.get(s.replace(".yaml", "").split("-")[-1], 4), s)

def fetch_all_files(target, ROOT="overleaf/kubernetes/"):
    p = Path(ROOT)
    files_with_web = [file for file in p.glob('*{}*'.format(target)) if file.is_file()]
    res = []
    for file in files_with_web:
        res.append(str(file))
    res = sorted(res, key=custom_sort)
    return res

def cpu(value):
  """
  Return CPU in milicores if it is configured with value
  """
  if re.match(r"[0-9]{1,9}m", str(value)):
    cpu = re.sub("[^0-9]", "", value)
  elif re.match(r"[0-9]{1,4}$", str(value)):
    cpu = int(value) * 1000
  elif re.match(r"[0-9]{1,15}n", str(value)):
    cpu = int(re.sub("[^0-9]", "", value)) // 1000000
  elif re.match(r"[0-9]{1,15}u", str(value)):
    cpu = int(re.sub("[^0-9]", "", value)) // 1000
  return int(cpu)

def memory(value):
  """
  Return Memory in MB
  """
  if re.match(r"[0-9]{1,9}Mi?", str(value)):
    mem = re.sub("[^0-9]", "", value)
  elif re.match(r"[0-9]{1,9}Ki?", str(value)):
    mem = re.sub("[^0-9]", "", value)
    mem = int(mem) // 1024
  elif re.match(r"[0-9]{1,9}Gi?", str(value)):
    mem = re.sub("[^0-9]", "", value)
    mem = int(mem) * 1024
  return int(mem)

if __name__ == "__main__":
    fetch_all_files("docstore")
    
if __name__ == "__main__":
  s = "asid"
  s = s.upper()
  print(s)
  # manifests = fetch_all_files("contacts")
  # print(manifests)
  # initiate_pod(manifests, "contacts", "one")