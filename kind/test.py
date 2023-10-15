from kubernetes import client, config

def list_pods_and_labels():
    # Load Kubernetes configuration from the default location
    config.load_kube_config()

    # Create a Kubernetes API client
    api = client.CoreV1Api()

    # List all pods in the cluster
    pods = api.list_pod_for_all_namespaces(watch=False)

    # Iterate through the pods and print their labels
    for pod in pods.items:
        if 'clsi' in pod.metadata.name:
            pod_name = pod.metadata.name
            namespace = pod.metadata.namespace
            node_labels = pod.metadata.labels["node"]
            print(f"Pod Name: {pod_name}, Namespace: {namespace}, Labels: {node_labels}")

if __name__ == "__main__":
    list_pods_and_labels()