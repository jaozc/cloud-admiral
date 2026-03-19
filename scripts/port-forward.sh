#!/bin/bash
kubectl port-forward svc/prometheus-server 9090:80 -n monitoring &
kubectl port-forward svc/grafana            3000:80 -n monitoring &
kubectl port-forward svc/elasticsearch-master 9200:9200 -n monitoring &
echo "Services available at:"
echo "  Prometheus:    http://localhost:9090"
echo "  Grafana:       http://localhost:3000"
echo "  ElasticSearch: http://localhost:9200"
wait $!