# AgentRegistry Documentation

## Overview

The `AgentRegistry` is a singleton class that provides a centralized way to register, store, and retrieve agents in your trading card game application. It uses a thread-safe singleton pattern to ensure only one registry exists across the application.

## Features

- **Singleton Pattern**: Ensures only one registry instance exists
- **Thread-Safe**: All operations are protected by locks
- **Dictionary-like Interface**: Supports `[]` access, iteration, and containment checks
- **Bulk Operations**: Register multiple agents at once
- **Error Handling**: Comprehensive error handling with descriptive messages
- **Flexible Retrieval**: Get agents with or without exceptions

## Basic Usage

### Import and Initialize

```python
from agent_registry import agent_registry

# The registry is automatically initialized as a singleton
# No need to create instances manually
```

### Registering Agents

```python
from agents import Agent

# Create an agent
my_agent = Agent(
    name="My Agent",
    instructions="Process some data...",
    tools=[...],
    output_type=...
)

# Register the agent
agent_registry.register_agent("my_agent", my_agent)

# Or register multiple agents at once
agents_to_register = {
    "agent1": agent1,
    "agent2": agent2,
    "agent3": agent3
}
agent_registry.register_multiple_agents(agents_to_register)
```

### Retrieving Agents

```python
# Get agent (returns None if not found)
agent = agent_registry.get_agent("my_agent")

# Get agent (raises KeyError if not found)
agent = agent_registry.get_agent_or_raise("my_agent")

# Dictionary-style access
agent = agent_registry["my_agent"]  # Raises KeyError if not found
```

### Checking Agent Existence

```python
# Check if agent exists
if agent_registry.has_agent("my_agent"):
    agent = agent_registry.get_agent("my_agent")

# Using 'in' operator
if "my_agent" in agent_registry:
    agent = agent_registry["my_agent"]
```

### Listing and Counting Agents

```python
# Get all agent names
agent_names = agent_registry.list_agents()

# Get total count
count = len(agent_registry)
count = agent_registry.get_agent_count()

# Get all agents as dictionary
all_agents = agent_registry.get_all_agents()
```

### Iterating Over Agents

```python
# Iterate over agent names
for agent_name in agent_registry:
    agent = agent_registry[agent_name]
    print(f"{agent_name}: {agent.name}")

# Iterate over all agents
for name, agent in agent_registry.get_all_agents().items():
    print(f"{name}: {agent.name}")
```

### Unregistering Agents

```python
# Unregister a specific agent
if agent_registry.unregister_agent("my_agent"):
    print("Agent unregistered successfully")
else:
    print("Agent not found")

# Clear all agents
agent_registry.clear()
```

## Advanced Usage

### Error Handling

```python
try:
    agent = agent_registry.get_agent_or_raise("non_existent_agent")
except KeyError as e:
    print(f"Agent not found: {e}")

try:
    agent_registry.register_agent("existing_agent", new_agent)
except ValueError as e:
    print(f"Registration failed: {e}")
```

### Dynamic Agent Management

```python
# Replace an existing agent
if agent_registry.has_agent("old_agent"):
    old_agent = agent_registry.get_agent("old_agent")
    agent_registry.unregister_agent("old_agent")
    
    # Create new agent with updated configuration
    new_agent = Agent(
        name="Updated Agent",
        instructions="New instructions...",
        tools=old_agent.tools,
        output_type=old_agent.output_type
    )
    
    agent_registry.register_agent("old_agent", new_agent)
```

### Configuration Management

```python
# Get agent configurations
all_agents = agent_registry.get_all_agents()

for name, agent in all_agents.items():
    print(f"Agent: {name}")
    print(f"  Name: {agent.name}")
    print(f"  Tools: {len(agent.tools) if hasattr(agent, 'tools') else 0}")
    print(f"  Output Type: {hasattr(agent, 'output_type')}")
    print(f"  Handoffs: {len(agent.handoffs) if hasattr(agent, 'handoffs') else 0}")
```

## Integration with Existing Code

### Refactoring Global Agents

Instead of having global agent variables:

```python
# Before
trigger_agent = Agent(...)
effect_agent = Agent(...)
target_agent = Agent(...)

# After
agent_registry.register_agent("trigger_parser", Agent(...))
agent_registry.register_agent("effect_parser", Agent(...))
agent_registry.register_agent("target_parser", Agent(...))
```

### Using Agents in Functions

```python
# Before
async def generate_ability(ability_description: str):
    Trigger_res, Effect_res, Target_res = await asyncio.gather(
        Runner.run(trigger_agent, ability_description),
        Runner.run(effect_agent, ability_description),
        Runner.run(target_agent, ability_description),
    )

# After
async def generate_ability(ability_description: str):
    trigger_agent = agent_registry.get_agent_or_raise('trigger_parser')
    effect_agent = agent_registry.get_agent_or_raise('effect_parser')
    target_agent = agent_registry.get_agent_or_raise('target_parser')
    
    Trigger_res, Effect_res, Target_res = await asyncio.gather(
        Runner.run(trigger_agent, ability_description),
        Runner.run(effect_agent, ability_description),
        Runner.run(target_agent, ability_description),
    )
```

## Benefits

1. **Centralized Management**: All agents in one place
2. **Dynamic Configuration**: Easy to swap agents at runtime
3. **Better Organization**: Clear naming and categorization
4. **Thread Safety**: Safe for concurrent access
5. **Error Prevention**: Built-in validation and error handling
6. **Flexibility**: Easy to add/remove agents without code changes
7. **Testing**: Easier to mock and test individual agents

## Best Practices

1. **Use Descriptive Names**: Choose clear, descriptive names for agents
2. **Handle Errors**: Always handle potential KeyError exceptions
3. **Check Existence**: Use `has_agent()` before accessing agents
4. **Clean Up**: Unregister agents when they're no longer needed
5. **Documentation**: Document agent purposes and configurations
6. **Consistent Naming**: Use consistent naming conventions across your application

## Examples

See the following files for complete examples:
- `agent_registry_example.py`: Basic usage examples
- `agent_registry_integration.py`: Integration with existing code

## Thread Safety

All operations in the `AgentRegistry` are thread-safe. The class uses a `threading.Lock()` to ensure that only one thread can modify the registry at a time. This makes it safe to use in multi-threaded applications.

## Performance Considerations

- The registry uses a simple dictionary for storage, providing O(1) average case lookup
- Thread locks add minimal overhead for most use cases
- The singleton pattern ensures minimal memory usage
- Consider clearing unused agents to free memory in long-running applications 