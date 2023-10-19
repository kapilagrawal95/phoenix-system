from kubernetes import client, config, watch
import subprocess
import utils
import chaos
# clean everything related to phoenix
# i.e. all resources in the namespace label phoenix=enabled.


def start_all_kubelets(api):
    nodes = utils.get_nodes(api)
    for node in nodes:
        chaos.start_kubelet(node)
    
def delete_resources_in_namespaces_with_label(api, label_selector):
    # Load the Kubernetes configuration from the default location or your kubeconfig file
    config.load_kube_config()

    # Create a Kubernetes API client
    api = client.CoreV1Api()
    # List all namespaces with the specified label
    namespaces = api.list_namespace(label_selector=label_selector).items
    namespace_names = []
    for namespace in namespaces:
        namespace_name = namespace.metadata.name
        namespace_names.append(namespace_name)
        print("Deleting all resources in {}..".format(namespace_names))
        # List resources (Pods, Deployments, Services, etc.) in the namespace
        try:
            cmd = "kubectl delete all --all -n {}".format(namespace_name)
            output = subprocess.check_output(cmd, shell=True, text=True)
            print(output)
            cmd = "kubectl delete pvc --all -n {}".format(namespace_name)
            output = subprocess.check_output(cmd, shell=True, text=True)
            print(output)
            # cmd = "kubectl delete pv --all -n {}".format(namespace_name)
            # output = subprocess.check_output(cmd, shell=True, text=True)
            # print(output)
            
        except:
            print("some error deleting resource in namespace {}..".format(namespace_name))
    
    for ns in namespace_names:
        print("Deleting the namespace {}..".format(ns))
        try:
            cmd = "kubectl delete ns {}".format(ns)
            output = subprocess.check_output(cmd, shell=True, text=True)
        except:
            print("some error deleting the namespace {}..".format(namespace_name))
        
    

if __name__ == "__main__":
    config.load_kube_config()
    api = client.CoreV1Api()
    label_selector = "phoenix=enabled"
    start_all_kubelets(api)
    delete_resources_in_namespaces_with_label(api, label_selector)
