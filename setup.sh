#!/bin/bash

# install istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.19.1/
export PATH=$PWD/bin:$PATH
istioctl install
kubectl apply -f samples/addons/grafana.yaml
kubectl apply -f samples/addons/prometheus.yaml
kubectl apply -f samples/addons/kiali.yaml
kubectl apply -f samples/addons/jaeger.yaml

kubectl patch svc grafana -n istio-system -p '{"spec": {"type": "NodePort"}}'
kubectl patch svc kiali -n istio-system -p '{"spec": {"type": "NodePort"}}'
kubectl patch svc prometheus -n istio-system -p '{"spec": {"type": "NodePort"}}'

export GRAFANA_PORT=$(kubectl get svc grafana -n istio-system -o=jsonpath='{.spec.ports[0].nodePort}')
export KIALI_PORT=$(kubectl get svc kiali -n istio-system -o=jsonpath='{.spec.ports[0].nodePort}')
export PROMETHEUS_PORT=$(kubectl get svc prometheus -n istio-system -o=jsonpath='{.spec.ports[0].nodePort}')
export IP=$(hostname -I | awk '{print $1}')
# echo "run kubectl get pods -n istio-system to see whether grafana, prometheus, kiali, jaeger, were installed."

echo "GRAFANA accessible on $IP:$GRAFANA_PORT"
echo "KIALI accessible on $IP:$KIALI_PORT"
echo "PROMETHEUS accessible on $IP:$PROMETHEUS_PORT"
