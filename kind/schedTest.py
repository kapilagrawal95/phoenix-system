import time
import random
import json

from kubernetes import client, config, watch

config.load_kube_config()
v1=client.CoreV1Api()

scheduler_name = "foobar"

def nodes_available():
    ready_nodes = []
    for n in v1.list_node().items:
            for status in n.status.conditions:
                if status.status == "True" and status.type == "Ready":
                    ready_nodes.append(n.metadata.name)
    return ready_nodes

def scheduler(name, node, namespace="default"):
    body=client.V1Binding()
        
    target=client.V1ObjectReference()
    target.kind='Node'
    target.apiVersion='v1'
    target.name= node
    
    meta=client.V1ObjectMeta()
    meta.name=name
    
    body.target=target
    body.metadata=meta
    
    try:
        # Method changed in clinet v6.0
        # return v1.create_namespaced_binding(body, namespace)
        # For v2.0
        res = v1.create_namespaced_binding_binding(name, namespace, body)
        if res:
            # print 'POD '+name+' scheduled and placed on '+node
            return True

    except Exception as a:
        print ("Exception when calling CoreV1Api->create_namespaced_binding: %s\n" % a)
        return False

if __name__ == "__main__":
    w = watch.Watch()
    print("here")
    # for event in w.stream(v1.list_namespaced_pod, 'overleaf'):
    #     # print("here23")
    #     if event['object'].status.phase == 'Running':
    #         print(event['object'].metadata.name)
    print(nodes_available()[-1])
    print(scheduler('real-time-89f46b97c-lbr9x', nodes_available()[-1], namespace="overleaf"))