

import time
from dotenv import load_dotenv
import os
from rich.console import Console
from rich.panel import Panel
from agent.core import CloudAdmiral
from collector.data_collector import ClusterSnapshot, DataCollector

load_dotenv()
console = Console()

def snapshot_to_text(snapshot: ClusterSnapshot) -> str:
    lines = [f"=== Cluster Snapshot at {snapshot.timestamp} ===\n"]

    if snapshot.unhealthy_pods:
        lines.append("Unhealthy Pods:\n")
        for pod in snapshot.unhealthy_pods:
            lines.append(f"- {pod['name']} in {pod['namespace']} (Status: {pod['status']}, Restarts: {pod['restarts']})")

    if snapshot.high_cpu_nodes:
        lines.append("High CPU Nodes:\n")
        for node in snapshot.high_cpu_nodes:
            lines.append(f"- {node['node']} (CPU Usage: {node['cpu_pct']}%)")

    if snapshot.recent_errors:
        lines.append("Recent Errors:\n")
        for error in snapshot.recent_errors:
            lines.append(f"- {error}")

    if snapshot.pending_pods:
        lines.append("Pending Pods:\n")
        for pod in snapshot.pending_pods:
            lines.append(f"- {pod['name']} in {pod['namespace']} (Status: {pod['status']}, Restarts: {pod['restarts']})")

    return "\n".join(lines)

def main():
    collector = DataCollector(
        prometheus_url=os.getenv("PROMETHEUS_URL", "http://localhost:9090"),
        elastic_url=os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    )

    agent = CloudAdmiral(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    interval = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    console.print(f"[bold green]Starting Cloud Admiral agent...[/bold green]")

    while True:
        try:
            console.print(f"[dim]Collecting cluster snapshot...[/dim]")
            snapshot = collector.collect()
            snapshot_text = snapshot_to_text(snapshot)

            console.print(Panel(snapshot_text, title="Snapshot", border_style="blue"))

            response = agent.analyze_and_act(snapshot_text)
            console.print(Panel(response, title="Response", border_style="green"))

        except Exception as e:
            console.print(f"[red]Error: {e}[/bold red]")
        
        time.sleep(interval)

if __name__ == "__main__":
    main()