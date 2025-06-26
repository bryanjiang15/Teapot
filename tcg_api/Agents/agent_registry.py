import threading
from typing import Dict, Optional, Any
from agents import Agent


class AgentRegistry:
    """
    A singleton registry for managing and retrieving agents.
    
    This class provides a centralized way to register, store, and retrieve
    agents by name. It uses a singleton pattern to ensure only one registry
    exists across the application.
    """
    
    _instance: Optional['AgentRegistry'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'AgentRegistry':
        """Ensure only one instance of AgentRegistry exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the registry with an empty agent store."""
        if not hasattr(self, '_initialized'):
            self._agents: Dict[str, Agent] = {}
            self._initialized = True
    
    def register_agent(self, name: str, agent: Agent) -> None:
        """
        Register an agent with the given name.
        
        Args:
            name (str): The name to register the agent under
            agent (Agent): The agent instance to register
            
        Raises:
            ValueError: If the name is already registered
        """
        with self._lock:
            if name in self._agents:
                raise ValueError(f"Agent with name '{name}' is already registered")
            self._agents[name] = agent
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Retrieve an agent by name.
        
        Args:
            name (str): The name of the agent to retrieve
            
        Returns:
            Optional[Agent]: The agent if found, None otherwise
        """
        with self._lock:
            return self._agents.get(name)
    
    def get_agent_or_raise(self, name: str) -> Agent:
        """
        Retrieve an agent by name, raising an exception if not found.
        
        Args:
            name (str): The name of the agent to retrieve
            
        Returns:
            Agent: The agent if found
            
        Raises:
            KeyError: If the agent is not found
        """
        agent = self.get_agent(name)
        if agent is None:
            raise KeyError(f"Agent with name '{name}' not found in registry")
        return agent
    
    def unregister_agent(self, name: str) -> bool:
        """
        Unregister an agent by name.
        
        Args:
            name (str): The name of the agent to unregister
            
        Returns:
            bool: True if the agent was unregistered, False if it wasn't found
        """
        with self._lock:
            if name in self._agents:
                del self._agents[name]
                return True
            return False
    
    def list_agents(self) -> list[str]:
        """
        Get a list of all registered agent names.
        
        Returns:
            list[str]: List of all registered agent names
        """
        with self._lock:
            return list(self._agents.keys())
    
    def has_agent(self, name: str) -> bool:
        """
        Check if an agent with the given name is registered.
        
        Args:
            name (str): The name to check
            
        Returns:
            bool: True if the agent is registered, False otherwise
        """
        with self._lock:
            return name in self._agents
    
    def clear(self) -> None:
        """Clear all registered agents."""
        with self._lock:
            self._agents.clear()
    
    def get_agent_count(self) -> int:
        """
        Get the total number of registered agents.
        
        Returns:
            int: Number of registered agents
        """
        with self._lock:
            return len(self._agents)
    
    def get_all_agents(self) -> Dict[str, Agent]:
        """
        Get a copy of all registered agents.
        
        Returns:
            Dict[str, Agent]: Dictionary mapping agent names to agent instances
        """
        with self._lock:
            return self._agents.copy()
    
    def register_multiple_agents(self, agents: Dict[str, Agent]) -> None:
        """
        Register multiple agents at once.
        
        Args:
            agents (Dict[str, Agent]): Dictionary mapping names to agents
            
        Raises:
            ValueError: If any of the names are already registered
        """
        with self._lock:
            # Check for conflicts first
            for name in agents:
                if name in self._agents:
                    raise ValueError(f"Agent with name '{name}' is already registered")
            
            # Register all agents
            self._agents.update(agents)
    
    def __contains__(self, name: str) -> bool:
        """Check if an agent with the given name is registered."""
        return self.has_agent(name)
    
    def __getitem__(self, name: str) -> Agent:
        """Get an agent by name using dictionary-style access."""
        return self.get_agent_or_raise(name)
    
    def __setitem__(self, name: str, agent: Agent) -> None:
        """Register an agent using dictionary-style access."""
        self.register_agent(name, agent)
    
    def __delitem__(self, name: str) -> None:
        """Unregister an agent using dictionary-style access."""
        if not self.unregister_agent(name):
            raise KeyError(f"Agent with name '{name}' not found in registry")
    
    def __len__(self) -> int:
        """Get the number of registered agents."""
        return self.get_agent_count()
    
    def __iter__(self):
        """Iterate over registered agent names."""
        return iter(self.list_agents())


# Global instance for easy access
agent_registry = AgentRegistry()
