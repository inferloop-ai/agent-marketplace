class Executor:
    """
    Base class for all executors.
    """

    def __init__(self, engine: Engine):
        self.engine = engine

    async def execute(self, agent: Agent, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with the given inputs.

        Args:
        - agent (Agent): The agent to execute.
        - inputs (Dict[str, Any]): The inputs to pass to the agent.

        Returns:
        - Dict[str, Any]: The outputs of the agent.
        """
        raise NotImplementedError
