import re
from pathlib import Path
import yaml

import subprocess
import os

def initiate_pod(manifest_files, deployment_name, node_name):
    # cmd = f"kubectl apply -f overleaf/kubernetes/contacts-pv.yaml"
    # subprocess.check_call(cmd, shell=True)
    # Set the environment variable
    pv_claim_var = str(deployment_name.upper() + "_CLAIMNAME").replace("-", "_")
    node_var = str(deployment_name.upper() + "_NODE").replace("-", "_")
    for file in manifest_files:
      if "pv" in file:
        pvc_cmd = "kubectl get pvc | grep '^{}' | awk '{}'".format(deployment_name, "{print $1}")
        output = subprocess.check_output(pvc_cmd, shell=True)
        output = output.decode("utf-8").strip()
        for i in range(0, 9):
          pvc_name = "{}-claim{}".format(deployment_name, i)
          if pvc_name not in output:
            break
        os.environ[pv_claim_var] = pvc_name
        envsubst_command = ["envsubst < {} | kubectl apply -f -".format(file)]
        output = subprocess.check_output(envsubst_command, shell=True, text=True)
      elif "deployment" in file:
        os.environ[pv_claim_var] = pvc_name
        os.environ[node_var] = str(node_name)
        envsubst_command = ["envsubst < {} | kubectl apply -f -".format(file)]
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