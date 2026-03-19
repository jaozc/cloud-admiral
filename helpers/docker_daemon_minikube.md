# Point your local Docker to the Minikube Docker daemon
```bash
eval $(minikube docker-env)
```

# Verify it worked (you should see Minikube images)
```bash
docker images
```

# Switch back to your machine's normal Docker
```bash
eval $(minikube docker-env --unset)
```