#!/bin/bash

set -e

echo "===> Adding HELM repos"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana             https://grafana.github.io/helm-charts
helm repo add elastic             https://helm.elastic.co
helm repo add fluent              https://fluent.github.io/helm-charts
helm repo update

echo "==> Creating namespace"
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

echo "==> Installing Prometheus (lightweight version for Minikube)"
helm upgrade --install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --set alertmanager.enabled=false \
  --set prometheus-pushgateway.enabled=false \
  --set server.persistentVolume.enabled=false \
  --set server.resources.requests.memory=256Mi \
  --set server.resources.limits.memory=512Mi \
  --wait

echo "==> Installing Grafana"
helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --set persistence.enabled=false \
  --set resources.requests.memory=128Mi \
  --set resources.limits.memory=256Mi \
  --set adminPassword=admin123 \
  --wait

echo "==> Installing ElasticSearch (single-node for dev)"
helm upgrade --install elasticsearch elastic/elasticsearch \
  --namespace monitoring \
  --set replicas=1 \
  --set minimumMasterNodes=1 \
  --set resources.requests.memory=512Mi \
  --set resources.limits.memory=1Gi \
  --set persistence.enabled=false \
  --set secret.password=elastic123 \
  --wait

echo "==> Installing FluentBit"
helm upgrade --install fluent-bit fluent/fluent-bit \
  --namespace monitoring \
  --set resources.requests.memory=32Mi \
  --set resources.limits.memory=64Mi \
  --wait

echo ""
echo "Observability stack installed successfully!"
echo "Prometheus: kubectl port-forward svc/prometheus-server 9090:80 -n monitoring"
echo "Grafana:    kubectl port-forward svc/grafana 3000:80 -n monitoring  (admin / admin123)"