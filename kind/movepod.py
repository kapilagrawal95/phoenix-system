
import subprocess
import os

def initiate_pod(manifest_file, node_name):
    
    # cmd = f"kubectl apply -f overleaf/kubernetes/contacts-pv.yaml"
    # subprocess.check_call(cmd, shell=True)
    # Set the environment variable
    os.environ["CONTACTS_NODE"] = str(node_name)
    # manifest_file = "overleaf/kubernetes/contacts-deployment.yaml"
    envsubst_command = ["envsubst < {} | kubectl apply -f -".format(manifest_file)]
    output = subprocess.check_output(envsubst_command, shell=True, text=True)
    return output