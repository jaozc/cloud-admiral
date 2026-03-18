# ⚓ Cloud Admiral

<p align="center">
  <img src="assets/logo.png" alt="Cloud Admiral Logo" width="500">
</p>

Cloud Admiral is an intelligent AI agent designed to simplify and optimize Kubernetes management. By leveraging Large Language Models (LLMs), it acts as a virtual "commander" for your clusters, capable of understanding natural language intent and translating it into efficient K8s operations.

---

## 🌟 Key Features

* **Natural Language Interface:** Interact with your cluster using plain English (or Portuguese) instead of complex YAML/kubectl commands.
* **Intelligent Self-Healing:** The agent monitors pod health and suggests/executes remediation steps based on logs and metrics analysis.
* **IoT & Edge Aware:** Optimized for orchestration in constrained environments (perfect for MicroK8s and K3s).
* **Contextual Insights:** Get high-level summaries of cluster health, resource utilization, and potential bottlenecks.

## 🛠 Tech Stack

* **Language:** Python (FastAPI/LangChain)
* **Orchestration:** Kubernetes (Support for EKS, MicroK8s, and K3s)
* **AI Engine:** OpenAI GPT-4o / Local LLMs via Ollama
* **Infrastructure:** Docker, Helm

## 🚀 Getting Started

### Prerequisites
- Kubernetes Cluster (v1.24+)
- Python 3.11+
- OpenAI API Key (or a local LLM instance)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jgzc/cloud-admiral.git
   cd cloud-admiral
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edite .env com seu Kubeconfig e chaves de API
   ```

4. Execute o agente:
   ```bash
   python main.py
   ```

## 🏗 Architecture
Cloud Admiral operates as a controller inside or outside the cluster, utilizing a Reasoning Loop (ReAct pattern) to:

- Observe the cluster state.
- Analyze logs/metrics using the LLM.
- Formulate and execute kubectl actions.

## 🎓 Academic Context
This project is part of my research at the Institute of Mathematical and Computer Sciences (ICMC - USP), focusing on intelligent orchestration for IoT and distributed systems.

## 📜 License
Distributed under the APACHE 2.0 License. See LICENSE for more information.