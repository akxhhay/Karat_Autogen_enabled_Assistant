from autogen import UserProxyAgent


def create_orchestrator(work_dir: str):
    """
    Orchestrator initiates chats and executes tool functions on behalf of agents.
    human_input_mode="NEVER" to run unattended. Switch to "ALWAYS" to approve each step.
    """
    orchestrator = UserProxyAgent(
        name="Orchestrator",
        human_input_mode="NEVER",
        code_execution_config={
            "work_dir": work_dir,
            "use_docker": False,  # set True if you want sandboxed execution
        },
    )
    return orchestrator