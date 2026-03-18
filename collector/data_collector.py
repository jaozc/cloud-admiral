

from dataclasses import dataclass
from datetime import datetime
from time import timezone
from kubernetes import client, config
from prometheus_api_client import PrometheusConnect
from elasticsearch import Elasticsearch

@dataclass
class ClusterSnapshot:
    timestamp: str
    unhealthy_pods: list[dict]
    high_cpu_nodes: list[dict]
    recent_errors: list[str]
    pending_pods: list[dict]


class DataCollector:
    def __init__(self, prometheus_url: str, elastic_url: str):
        # Configure Kubernetes client
        config.load_kube_config()
        self.k8s_v1 = client.CoreV1Api()
        self.k8s_apps = client.AppsV1Api()

        # Initialize Prometheus client
        self.prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)

        # Initialize Elasticsearch client
        self.es = Elasticsearch(elastic_url)

    def get_unhealthy_pods(self) -> list[dict]:
        """Get all unhealthy pods from the cluster"""
        pods = self.k8s_v1.list_pod_for_all_namespaces().items
        return [
            {
                "name": p.metadata.name,
                "namespace": p.metadata.namespace,
                "status": p.status.phase,
                "restates": sum(
                    cs.restart_count for cs in (p.status.container_statuses or [])
                )
            } for p in pods if p.status.phase not in ("Running", "Succeeded", "Pending")
        ]

    def get_high_cpu_nodes(self, threshold: float = 80.0) -> list[dict]:
        """Get all nodes with CPU usage above the threshold with Prometheus"""
        query = '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
        result = self.prom.custom_query(query)
        return [
            {"node": r["metric"]["instance"], "cpu_pct": float(r["value"][1])}
            for r in result
            if float(r["value"][1]) > threshold
        ]

    def get_recent_errors(self, minutes: int = 10) -> list[str]:
        """Search for recent error logs in ElasticSearch."""
        resp = self.es.search(
            index="k8s-logs-*",
            body={
                "query": {
                    "bool": {
                        "must": [{"match": {"level": "ERROR"}}],
                        "filter": [{"range": {"@timestamp": {"gte": f"now-{minutes}m"}}}]
                    }
                },
                "size": 20,
                "_source": ["message", "kubernetes.pod_name"]
            }
        )
        return [hit["_source"]["message"] for hit in resp["hits"]["hits"]]
        
    def collect(self) -> ClusterSnapshot:
        """Collect data from the cluster and return a ClusterSnapshot"""
        return ClusterSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            unhealthy_pods=self.get_unhealthy_pods(),
            high_cpu_nodes=self.get_high_cpu_nodes(),
            recent_errors=self.get_recent_errors(),
            pending_pods=[]
        )