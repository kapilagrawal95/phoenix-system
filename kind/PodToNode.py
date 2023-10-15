from kubernetes import client, config

# Load the Kubernetes configuration (usually located at ~/.kube/config)
config.load_kube_config()

# Create a V1Pod object
pod = client.V1Pod(
    metadata=client.V1ObjectMeta(name="clsi"),
    spec=client.V1PodSpec(
        containers=[
            client.V1Container(
                name="clsi",
                image="gtato/sharelatex-clsi",
            )
        ],
        affinity=client.V1Affinity(
            node_affinity=client.V1NodeAffinity(
                required_during_scheduling_ignored_during_execution=client.V1NodeSelector(
                    node_selector_terms=[
                        client.V1NodeSelectorTerm(
                            match_expressions=[
                                client.V1NodeSelectorRequirement(
                                    key="kubernetes.io/hostname",
                                    operator="In",
                                    values=["kind-worker2"],
                                )
                            ]
                        )
                    ]
                )
            )
        )
    )
)

# Create a V1Pod object in the Kubernetes cluster
api_instance = client.CoreV1Api()
api_instance.create_namespaced_pod(body=pod, namespace="overleaf")

print("Pod scheduled to a specific node.")
