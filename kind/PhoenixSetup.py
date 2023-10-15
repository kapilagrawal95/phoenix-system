# import yaml
# from kubernetes import client, config
# from kubernetes.client import V1Affinity, V1NodeSelector, V1NodeSelectorTerm, V1NodeSelectorRequirement

# def apply_node_affinity_to_yaml(yaml_file_path, node_label, desired_node):
#     # Load the Kubernetes configuration
#     config.load_kube_config()

#     with open(yaml_file_path, 'r') as file:
#         # Load the original YAML manifest
#         resource_manifest = yaml.safe_load(file)

#     if 'kind' not in resource_manifest:
#         print("Error: Unknown resource type in the YAML file.")
#         return

#     if resource_manifest['kind'] != 'Pod':
#         print("Error: Only Pods are supported for node affinity.")
#         return

#     # Create node affinity rules
#     node_affinity = V1Affinity(
#         node_affinity=V1NodeAffinity(
#             required_during_scheduling_ignored_during_execution=[V1NodeSelectorTerm(
#                 match_expressions=[V1NodeSelectorRequirement(
#                     key=node_label,
#                     operator="In",
#                     values=[desired_node]
#                 )]
#             )]
#         )
#     )

#     # Add the node affinity to the Pod spec
#     resource_manifest['spec']['affinity'] = node_affinity

#     # Create a Kubernetes API client
#     api = client.CoreV1Api()

#     # Apply the updated YAML to create or update the Pod
#     api.create_namespaced_pod(namespace=resource_manifest['metadata']['namespace'], body=resource_manifest)

# if __name__ == "__main__":
#     yaml_file_path = "overleaf/kubernetes/clsi-deployment.yaml"  # Replace with the path to your YAML file
#     node_label = "kind-worker"  # Specify the node label for node affinity
#     desired_node = "desired-node"  # Specify the node you want to target

#     apply_node_affinity_to_yaml(yaml_file_path, node_label, desired_node)



# from kubernetes import client, config
# config.load_kube_config()
# api = client.AppsV1Api()

# # read current state
# deployment = api.read_namespaced_deployment(name='clsi', namespace='overleaf')

# # check current state
# #print(deployment.spec.template.spec.affinity)

# # create affinity objects
# terms = client.models.V1NodeSelectorTerm(
#     match_expressions=[
#         {'key': 'kind-worker3',
#          'operator': 'In',
#          'values': [""]}
#     ]
# )
# node_selector = client.models.V1NodeSelector(node_selector_terms=[terms])
# node_affinity = client.models.V1NodeAffinity(
#     required_during_scheduling_ignored_during_execution=node_selector
# )
# affinity = client.models.V1Affinity(node_affinity=node_affinity)

# # replace affinity in the deployment object
# deployment.spec.template.spec.affinity = affinity

# # finally, push the updated deployment configuration to the API-server
# api.replace_namespaced_deployment(name=deployment.metadata.name,
#                                   namespace=deployment.metadata.namespace,
#                                   body=deployment)

# from kubernetes import client, config, utils

# def main():
#     config.load_kube_config()
#     k8s_client = client.ApiClient()
#     yaml_file = 'overleaf/kubernetes/clsi-deployment.yaml'
#     utils.create_from_yaml(k8s_client,yaml_file,verbose=True,namespace="overleaf")

# if __name__ == "__main__":
#     main()

from kubernetes import config, client, utils

# Load the Kubernetes configuration (usually located at ~/.kube/config)
config.load_kube_config()

import
class Loader(yaml.loader.SafeLoader):
    yaml_implicit_resolvers = yaml.loader.SafeLoader.yaml_implicit_resolvers.copy()
    if "=" in yaml_implicit_resolvers:
        yaml_implicit_resolvers.pop("=")
            
def schedule_pod_to_node(manifest_path, node_name, namespace="overleaf"):
    try:
        with open(manifest_path, 'r') as file:
            pod_manifest = file.read()
            
        p
        # Load the manifest as a V1Pod object
        pod = utils.create_from_dict(client.ApiClient(), client.ApiClient().sanitize_for_serialization(pod_manifest))

        # Create the pod in the Kubernetes cluster
        api_instance = client.CoreV1Api()
        api_instance.create_namespaced_pod(body=pod, namespace=namespace)

        # Create a binding to schedule the pod to the specified node
        binding = client.V1Binding(target=client.V1ObjectReference(node_name=node_name))
        api_instance.create_namespaced_binding(
            namespace=namespace,
            name=pod.metadata.name,
            body=binding
        )

        print(f"Pod scheduled to node {node_name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    manifest_file = "overleaf/kubernetes/clsi-deployment.yaml"  # Replace with the path to your manifest file
    target_node = "kind-worker3"    # Replace with the name of the target node
    schedule_pod_to_node(manifest_file, target_node)
