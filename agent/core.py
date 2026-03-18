

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from .tools.k8s_tools import restart_deployment, scale_deployment, get_pod_logs, describe_pod


SYSTEM_PROMPT = """You are a Kubernetes operations specialist agent.
Your role is to analyze the cluster state and take precise corrective actions.

Mandatory safety rules:
- ALWAYS inspect logs and describe the pod before restarting it
- NEVER scale above 10 replicas without explicit justification
- NEVER delete resources, only restart or scale
- In case of doubt, prefer observing and reporting instead of acting
- Record the reasoning for each action taken

When receiving a cluster snapshot, analyze:
1. Unhealthy pods (CrashLoopBackOff, OOMKilled, etc.)
2. Nodes with high resource usage
3. Error patterns in recent logs
4. Usage trends (is it getting worse or better?)

Respond always in English, being objective and technical."""


class CloudAdmiral:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=openai_api_key,
            temperature=0.0,
        )
        self.tools = [
            restart_deployment,
            scale_deployment,
            get_pod_logs,
            describe_pod
        ]
        
        self.memory = ConversationBufferWindowMemory(
            k=10, # keep last 10 messages
            memory_key="chat_history",
            return_messages=True,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)

        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            prompt=prompt,
            memory=self.memory,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
        )

    def analyze_and_act(self, snapshot_text: str) -> str:
        """Analyze the cluster snapshot and take corrective actions."""
        return self.executor.invoke({"input": snapshot_text})["output"]
