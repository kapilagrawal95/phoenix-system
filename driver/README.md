Driver Design

Inputs:
1. Number of Nodes
2. Workloads and copies of each workload.

Functions;
1. Should run a cloudlab cluster if nodes are five no more than 30 nodes (assuming 40% nodes will be of kube-system) -- only counting worker nodes
2. Should take which workloads to run and how many copies (workloads are hotelres and overleaf, copies can be say 3,5 which means 3 copies of hotel res and 5 copies of overleaf)
3. Should allocate each app to one namespace and label the namespace as phoenix=enabled.
4. Should make two partitions say if there are 5 nodes then out of 5 two should be reserved for stateful pods only. Each node can only have upto 6 pods so 12 stateful pods are possible. This is not going to be destroyed in our experiments.
5. Pod placements will only be handled by node affinity rules set bu environment variables.
