# 1) Point Docker to Minikube's Docker daemon
```bash
eval $(minikube docker-env)
```

# 2) Build the image inside Minikube
```bash
docker build -t k8s-ai-agent:latest .
```

# 3) Install or upgrade the agent chart
#    Secrets are passed via CLI (do not commit them to git).
```bash
helm upgrade --install k8s-ai-agent ./helm/agent \
  --namespace monitoring \
  --create-namespace \
  --set secrets.openaiApiKey="<YOUR_OPENAI_API_KEY>" \
  --set secrets.elasticPassword="<YOUR_ELASTIC_PASSWORD>"
```

# 4) Tail the logs (label selector: `app=k8s-ai-agent`)
```bash
kubectl logs -n monitoring -l app=k8s-ai-agent -f
```

# (Optional) Switch Docker back to your machine
```bash
eval $(minikube docker-env --unset)
```