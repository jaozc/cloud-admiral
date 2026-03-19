import os
from typing import Any, List, Optional, Union, Dict
from typing_extensions import TypedDict

# Modern imports for v1.x
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import AgentMiddleware, SummarizationMiddleware
from langchain_core.messages import trim_messages, BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime

from agent.guardrails import requires_approval

# Tools remain imported from the local module structure
from.tools.k8s_tools import restart_deployment, scale_deployment, get_pod_logs, describe_pod

# Refined System Prompt (Logic remains identical to original)
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

class TrimmingMiddleware(AgentMiddleware):
    """
    Custom middleware to implement the 'k=10' window requirement.
    Replaces the legacy ConversationBufferWindowMemory.
    """
    def before_model(self, state: AgentState, runtime: Runtime) -> Optional[Dict[str, Any]]:
        messages = state.get("messages",)
        
        # We target k=11 to include the System Prompt + 10 turns.
        # token_counter=len allows us to count messages directly as requested.
        trimmed_history = trim_messages(
            messages,
            max_tokens=11, 
            strategy="last",
            token_counter=len,
            include_system=True,
            start_on="human"
        )
        
        # In v1.x middleware, returning a dict updates the model request's context
        return {"messages": trimmed_history}

class GuardrailsMiddleware(AgentMiddleware):
    """
    Custom middleware to implement the guardrails logic.
    """
    def before_model(self, state: AgentState, runtime: Runtime) -> Optional[Dict[str, Any]]:
        messages = state.get("messages",)
        last_message = messages[-1]
        if last_message.tool_calls:
            tool_call = last_message.tool_calls[0]
            tool_name = tool_call.function.name
            args = tool_call.function.arguments
            if requires_approval(tool_name, args):
                return {
                    "messages": [
                        {"role": "user", "content": f"Please approve the following action: {tool_name} with args: {args}"}
                    ]
                }
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> Optional[Dict[str, Any]]:
        messages = state.get("messages",)
        return {"messages": messages}

class CloudAdmiral:
    def __init__(self, openai_api_key: str):
        # Initialize the model with modern v1 parameters
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=openai_api_key,
            temperature=0.0,
            # OpenAI specific optimization for tool use
            # use_responses_api=True  # Optional: For advanced reasoning models
        )
        
        # Tools can be passed as a list of LangChain tools or callables
        self.tools = [
            restart_deployment,
            scale_deployment,
            get_pod_logs,
            describe_pod
        ]
        
        # Persistence: InMemorySaver replaces the 'memory' object.
        # This provides thread-level persistence for multi-turn conversations.
        self.checkpointer = InMemorySaver()

        # create_agent is the modern standard for building agents in v1.x.
        # It replaces AgentExecutor and create_tool_calling_agent.
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
            # Middleware hooks for context management and safety
            middleware=[TrimmingMiddleware(), GuardrailsMiddleware()],
            checkpointer=self.checkpointer,
            max_iterations=5,
            handle_errors=True # Replaces handle_parsing_errors
        )

    def analyze_and_act(self, snapshot_text: str, thread_id: str = "cluster-analysis-01") -> str:
        """
        Analyze the cluster snapshot and take corrective actions.
        Now requires a thread_id to support persistent conversation history.
        """
        # Modern execution uses the thread_id for state retrieval
        config = {"configurable": {"thread_id": thread_id}}
        
        # The primary input key in v1.x AgentState is 'messages'
        input_data = {
            "messages": [
                {"role": "user", "content": snapshot_text}
            ]
        }
        
        # invoke() returns the full state after execution
        result = self.agent.invoke(input_data, config=config)
        
        # Return the content of the final AI message
        return result["messages"][-1].content