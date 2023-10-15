#!/bin/bash

# ensure that kind cluster (on docker) is running
kind create cluster --config kind/kind-config.yaml
sleep 10 # until kind cluster is running

kubectl label node kind-worker disktype=ssd
kubectl label node kind-worker2 disktype=none
kubectl label node kind-worker3 disktype=none
kubectl label node kind-worker worker=one
kubectl label node kind-worker2 worker=two
kubectl label node kind-worker3 worker=three
kubectl label node kind-worker4 worker=four


kubectl get nodes --show-labels
#setup metrics server: (Followed this link: https://gist.github.com/sanketsudake/a089e691286bf2189bfedf295222bd43)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.5.0/components.yaml
kubectl patch -n kube-system deployment metrics-server --type=json   -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

# log in into root cluster and first fetch the IP address of the cluster.
export IP=$(docker exec -it kind-control-plane /bin/bash -c "hostname -I | awk '{print $1}'" | cut -d ' ' -f 1) 

export SHARELATEX_REAL_TIME_URL_VALUE=$IP":30911" 
echo $SHARELATEX_REAL_TIME_URL_VALUE

export DOCSTORE_NODE=one
export DOCSTORE_CLAIMNAME=docstore-claim0
export FILESTORE_NODE=one
export FILESTORE_CLAIMNAME=filestore-claim0
export REDIS_NODE=one
export MONGO_NODE=one
export MONGO_CLAIMNAME=mongo-claim0
export WEB_NODE=one
export CONTACTS_NODE=two
export CONTACTS_CLAIMNAME=contacts-claim0
export CLSI_NODE=three
export DOCUMENT_UPDATER_NODE=four
export NOTIFICATIONS_NODE=two
export NOTIFICATIONS_CLAIMNAME=notifications-claim0
export REAL_TIME_NODE=three
export SPELLING_NODE=four
export SPELLING_CLAIMNAME=spelling-claim0
export TRACK_CHANGES_NODE=two
export TRACK_CHANGES_CLAIMNAME=track-changes-claim0
export CHAT_NODE=three
export TAGS_NODE=four
export TAGS_CLAIMNAME=tags-claim0


bash overleaf/launch.sh

# After everything is ready, we need to login into the web pod and create users.
# Step 1: Login into the kind-control-plane
docker exec -it kind-control-plane /bin/bash
apt-get update
apt-get install nano
apt-get install python3
apt-get install python3-pip
pip3 install requests
nano create_users.py # copy the create_users.py here
kubectl config set-context --current --namespace=overleaf
python3 create_users.py # for this to work first make sure that web has already started and check logs for any errors.
#logout


kubectl delete pod clsi-57f6dd4b9c-vmn4s --grace-period=0 --force
kubectl delete deployment clsi  --grace-period=0 --force

kubectl delete pod track-changes-55c6667488-4478r --grace-period=0 --force
kubectl delete deployment track-changes  --grace-period=0 --force