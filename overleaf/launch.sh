#!/bin/bash

kubectl create namespace overleaf
# kubectl label namespace overleaf istio-injection=enabled
kubectl config set-context --current --namespace=overleaf

cd overleaf/kubernetes
envsubst < "mongo-pv.yaml" | kubectl apply -f -
envsubst < "mongo-deployment.yaml" | kubectl apply -f -
kubectl apply -f mongo-service.yaml
envsubst < "redis-deployment.yaml" | kubectl apply -f -
kubectl apply -f redis-service.yaml
envsubst < "filestore-pv.yaml" | kubectl apply -f -
envsubst < "filestore-deployment.yaml" | kubectl apply -f -
kubectl apply -f filestore-service.yaml
envsubst < "docstore-pv.yaml" | kubectl apply -f -
envsubst < "docstore-deployment.yaml" | kubectl apply -f -
kubectl apply -f docstore-service.yaml
envsubst < "tags-pv.yaml" | kubectl apply -f -
envsubst < "tags-deployment.yaml" | kubectl apply -f -
kubectl apply -f tags-service.yaml
envsubst < "realtime-deployment.yaml" | kubectl apply -f -
kubectl apply -f realtime-service.yaml
sleep 10
envsubst < "contacts-pv.yaml" | kubectl apply -f -
envsubst < "contacts-deployment.yaml" | kubectl apply -f -
kubectl apply -f contacts-service.yaml
envsubst < "clsi-deployment.yaml" | kubectl apply -f -
kubectl apply -f clsi-service.yaml
envsubst < "document-updater-deployment.yaml" | kubectl apply -f -
kubectl apply -f document-updater-service.yaml
envsubst < "notifications-pv.yaml" | kubectl apply -f -
envsubst < "notifications-deployment.yaml" | kubectl apply -f -
kubectl apply -f notifications-service.yaml
envsubst < "spelling-pv.yaml" | kubectl apply -f -
envsubst < "spelling-deployment.yaml" | kubectl apply -f -
kubectl apply -f spelling-service.yaml
envsubst < "track-changes-pv.yaml" | kubectl apply -f -
envsubst < "track-changes-deployment.yaml" | kubectl apply -f -
kubectl apply -f track-changes-service.yaml
# sleep 10
# IP=$(IP=$(hostname -I | awk '{print $1}')
# )
# SHARELATEX_REAL_TIME_URL_VALUE=$IP":30911" 
envsubst < "web-deployment.yaml" | kubectl apply -f -
kubectl apply -f web-service.yaml
# 155.98.36.11:30911
# sleep 10

# echo "First check web logs and see if the server is listening"
# echo "Access overleaf at:"$IP":30910 ! wait but first create users from create_users script by logging into the master node!"
# echo "perform a get to "$IP":30911 this should say Cannot GET"
