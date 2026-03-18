from langchain.tools import tool
from kubernetes import client, config

config.load_kube_config()
apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()

@tool
def restart_deployment(namespace: str, deployment_name: str) -> str:
    """
    Restart a deployment in the given namespace doing a rolling restart.
    Use when pods are in CrashLoopBackOff or with a lot of Restarts.
    """
    import datetime
    patch = {
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "kubectl.kubernetes.io/restartedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }
                }
            }
        }
    }
    apps_v1.patch_namespaced_deployment(deployment_name, namespace, patch)
    return f"Deployment {deployment_name} in namespace {namespace} restarted successfully."

@tool
def scale_deployment(namespace: str, deployment_name: str, replicas: int) -> str:
    """
    Scale a deployment in the given namespace to the given number of replicas.
    Use to increase capacity when CPU/memory is high.
    Maximum allowed: 10 replicas. Minimum: 1.
    """
    replicas = max(1, min(10, replicas))
    patch = {
        "spec": {
            "replicas": replicas
        }
    }
    apps_v1.patch_namespaced_deployment(deployment_name, namespace, patch)
    return f"Deployment {deployment_name} in namespace {namespace} scaled to {replicas} replicas successfully."

@tool
def get_pod_logs(namespace: str, pod_name: str, lines: int = 50) -> str:
    """
    Get the last lines of logs from a specific pod.
    Use to investigate errors before taking actions.
    """
    logs = core_v1.read_namespaced_pod_log(
        pod_name, namespace, tail_lines=lines
    )
    return logs or "No logs available."

@tool
def describe_pod(namespace: str, pod_name: str) -> str:
    """
    Get detailed information about a pod (events, container status).
    Use for diagnosis before restarting or scaling.
    """
    pod = core_v1.read_namespaced_pod(pod_name, namespace)
    events = core_v1.list_namespaced_event(
        namespace,
        field_selector=f"involvedObject.name={pod_name}"
    ).items
    
    info = {
        "phase": pod.status.phase,
        "containers": [
            {"name": c.name, "ready": c.ready, "restarts": c.restart_count}
            for c in (pod.status.container_statuses or [])
        ],
        "events": [e.message for e in events[-5:]]
    }
    return str(info)