SAFE_ACTIONS = {"get_pod_logs", "describe_pod"}
APPROVAL_REQUIRED = {"restart_deployment", "scale_deployment"}

def requires_approval(tool_name: str, args: dict) -> bool:
    """Return True if the tool requires approval."""
    if tool_name in SAFE_ACTIONS:
        return False
    
    # Scale deployment to more than 5 replicas requires approval
    if tool_name == "scale_deployment" and args.get("replicas", 0) > 5:
        return True

    return tool_name in APPROVAL_REQUIRED