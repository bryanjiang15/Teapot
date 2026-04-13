"""
AgentRegistry — thread-safe singleton registry for managing AI agents.

Copied from CreatorAPI/Agents/agent_registry.py and adapted for TeapotAPI.
Provides a single source of truth for all game compilation agents.
"""
import threading
from typing import Dict, Optional

from agents import Agent


class AgentRegistry:
    """
    A singleton registry for managing and retrieving agents.

    Provides a centralized way to register, store, and retrieve agents by
    name. Uses a singleton pattern to ensure only one registry exists across
    the application.
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
        """Register an agent under the given name.

        Raises ValueError if the name is already taken.
        """
        with self._lock:
            if name in self._agents:
                raise ValueError(f"Agent with name '{name}' is already registered")
            self._agents[name] = agent

    def get_agent(self, name: str) -> Optional[Agent]:
        """Retrieve an agent by name, or None if not found."""
        with self._lock:
            return self._agents.get(name)

    def get_agent_or_raise(self, name: str) -> Agent:
        """Retrieve an agent by name; raise KeyError if not found."""
        agent = self.get_agent(name)
        if agent is None:
            raise KeyError(f"Agent with name '{name}' not found in registry")
        return agent

    def unregister_agent(self, name: str) -> bool:
        """Unregister an agent. Returns True if removed, False if not found."""
        with self._lock:
            if name in self._agents:
                del self._agents[name]
                return True
            return False

    def list_agents(self) -> list[str]:
        """Return a list of all registered agent names."""
        with self._lock:
            return list(self._agents.keys())

    def has_agent(self, name: str) -> bool:
        """Return True if an agent with the given name is registered."""
        with self._lock:
            return name in self._agents

    def clear(self) -> None:
        """Clear all registered agents."""
        with self._lock:
            self._agents.clear()

    def get_agent_count(self) -> int:
        """Return the number of registered agents."""
        with self._lock:
            return len(self._agents)

    def get_all_agents(self) -> Dict[str, Agent]:
        """Return a copy of all registered agents."""
        with self._lock:
            return self._agents.copy()

    def register_multiple_agents(self, agents: Dict[str, Agent]) -> None:
        """Register multiple agents at once.

        Raises ValueError if any name is already registered.
        """
        with self._lock:
            for name in agents:
                if name in self._agents:
                    raise ValueError(f"Agent with name '{name}' is already registered")
            self._agents.update(agents)

    def __contains__(self, name: str) -> bool:
        return self.has_agent(name)

    def __getitem__(self, name: str) -> Agent:
        return self.get_agent_or_raise(name)

    def __setitem__(self, name: str, agent: Agent) -> None:
        self.register_agent(name, agent)

    def __delitem__(self, name: str) -> None:
        if not self.unregister_agent(name):
            raise KeyError(f"Agent with name '{name}' not found in registry")

    def __len__(self) -> int:
        return self.get_agent_count()

    def __iter__(self):
        return iter(self.list_agents())


# Module-level singleton — import this everywhere agents are needed
agent_registry = AgentRegistry()
