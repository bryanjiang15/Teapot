"""
Integration example showing how to refactor tcg_server_exp.py to use AgentRegistry.

This file demonstrates how to organize and manage agents using the registry pattern
instead of having them as global variables.
"""

import asyncio
from agent_registry import agent_registry
from agents import Agent, Runner, function_tool, trace, AgentOutputSchema
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from abilityData import *
from abilityDefinitions import *
from tcg_api.AmountProcessors.amount_processing import check_amount_data, process_amount_queries, update_processed_amounts


def create_and_register_agents():
    """Create all agents and register them in the registry"""
    
    # Import function tools (assuming they exist in the original file)
    # These would be the same function tools from tcg_server_exp.py
    from tcg_server_exp import (
        trigger_schema_tool, effect_schema_tool, target_schema_tool, 
        requirement_schema_tool, get_valid_trigger_target_types,
        get_card_id, create_random_card_effect_schema, get_valid_effect_target_types
    )
    
    # Create agents
    trigger_agent = Agent(
        name="Trading Card Game Assistant", 
        instructions="""You are a helpful assistant for developing a trading card game. 
        The user will provide you with an card ability description, and you will identify what event triggers the ability and what target can trigger the ability.
        The triggerType is the event that causes the ability to activate, and the triggerTargets defines what target can cause the trigger to activate. TriggerTarget is NOT the target of the ability.
        The triggerTarget should be determined by the triggerType. Call the get_valid_trigger_target_types tool to get a list of valid trigger targets for the trigger type and select one.
        Output a JSON object of the trigger schema.
        """,
        tools=[
            trigger_schema_tool,
            get_valid_trigger_target_types,
        ],
        output_type=AgentOutputSchema(AbilityTrigger)
    )

    create_card_effect_agent = Agent(
        name="Trading Card Game Assistant",
        instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
        You are a helpful assistant for developing a trading card game.
        The user will provide you with an card ability description, and you will identify the effect of the ability and the amount of the effect.
        The effect is an action that creates a card somewhere. You need to identify the specific effect type, and what card is created.
        If the ability generate a specific card, call the get_card_id tool to get the card id of that card, and return the card id as value in the amountData.
        If the ability generate a random card, call the create_random_card_effect_schema tool to create the amountData.
        Output a JSON object of the effect schema.
        """,
        tools=[
            get_card_id,
            create_random_card_effect_schema
        ],
        output_type=AgentOutputSchema(AbilityEffect)
    )

    effect_agent = Agent(
        name="Trading Card Game Assistant", 
        instructions="""You are a helpful assistant for developing a trading card game. 
        The user will provide you with an card ability description, and you will identify the effect of the ability and the amount of the effect.
        The effect is the action that the ability performs.
        If the ability effect creates a card, handoff to create_card_effect_agent.
        Output a JSON object of the effect schema.
        """,
        tools=[
            effect_schema_tool,
        ],
        output_type=AgentOutputSchema(AbilityEffect),
        handoffs=[create_card_effect_agent]
    )

    target_agent = Agent(
        name="Trading Card Game Assistant",
        instructions="""You are a helpful assistant for developing a trading card game.
        The user will provide you with an card ability description, and you will identify the target of the ability that will be affected.
        The target is the target that the effect is applied to, NOT the target that causes the ability to activate or the target that determines the effect of the ability.
        The target should be determined by the effect type. Call the get_valid_target_types tool to get a list of valid target types for the effect type and select one.
        Output a JSON object of the target schema.
        """,
        tools=[
            target_schema_tool,
            get_valid_effect_target_types
        ],
        output_type=AgentOutputSchema(TargetData)
    )

    requirement_agent = Agent(
        name="Trading Card Game Assistant",
        instructions="""You are a helpful assistant for developing a trading card game.
        The user will provide you with an card ability description, and you will identify the abilities' requirement to activate.
        The requirement is the condition that must be met for the ability to activate when the ability is triggered, the requirement is NOT the trigger.
        If the ability has no requirement, return an empty JSON object.
        Output a JSON object of the requirement schema.
        """,
        tools=[
            requirement_schema_tool,
        ],
        output_type=AgentOutputSchema(AbilityRequirement)
    )

    # Register all agents
    agents_to_register = {
        "trigger_parser": trigger_agent,
        "effect_parser": effect_agent,
        "target_parser": target_agent,
        "requirement_parser": requirement_agent,
        "card_effect_creator": create_card_effect_agent
    }
    
    agent_registry.register_multiple_agents(agents_to_register)
    print(f"Registered {len(agents_to_register)} agents in registry")


async def generate_ability_with_registry(ability_description: str):
    """Refactored Generate_Ability function using AgentRegistry"""
    
    # Get agents from registry
    trigger_agent = agent_registry.get_agent_or_raise('trigger_parser')
    effect_agent = agent_registry.get_agent_or_raise('effect_parser')
    target_agent = agent_registry.get_agent_or_raise('target_parser')
    
    result = None
    with trace("Ability Configuration"):
        Trigger_res, Effect_res, Target_res = await asyncio.gather(
            Runner.run(trigger_agent, ability_description),
            Runner.run(effect_agent, ability_description),
            Runner.run(target_agent, ability_description),
        )

        print("Trigger result type:", Trigger_res.final_output)
        print("Amount result type:", Effect_res.final_output["amount"])
        print("Target result type:", Target_res.final_output)

        outputs = {
            "trigger": Trigger_res.final_output,
            "effect": Effect_res.final_output,
            "target": Target_res.final_output,
        }

        # Collect initial amount queries
        initial_queries = []
        for output_type, output in outputs.items():
            initial_queries.extend(await check_amount_data(output_type, output))
        
        # Process amount queries recursively
        processed_results = await process_amount_queries(initial_queries, target_agent)
        
        # Update outputs with processed results
        for output_type, output in outputs.items():
            await update_processed_amounts(output_type, output, processed_results)
        
        # Print final outputs
        for output in outputs.values():
            print(output)
        result = AbilityResponse(
            triggerDefinition=outputs["trigger"],
            targetDefinition=[outputs["target"]],
            effect=outputs["effect"]["effectType"],
            amount=outputs["effect"]["amount"],
        )
    return result


async def demonstrate_registry_benefits():
    """Demonstrate the benefits of using AgentRegistry"""
    print("=== AgentRegistry Benefits Demonstration ===")
    
    # 1. Easy agent discovery
    print(f"Available agents: {agent_registry.list_agents()}")
    
    # 2. Dynamic agent selection
    agent_types = ['trigger_parser', 'effect_parser', 'target_parser']
    selected_agents = {}
    
    for agent_type in agent_types:
        if agent_registry.has_agent(agent_type):
            selected_agents[agent_type] = agent_registry.get_agent(agent_type)
            print(f"Found {agent_type}: {selected_agents[agent_type].name}")
    
    # 3. Easy agent replacement/swapping
    print(f"\nAgent count before: {len(agent_registry)}")
    
    # Simulate replacing an agent
    if agent_registry.has_agent('trigger_parser'):
        old_agent = agent_registry.get_agent('trigger_parser')
        agent_registry.unregister_agent('trigger_parser')
        
        # Create a new version of the agent (in real scenario, this might be a different implementation)
        new_trigger_agent = Agent(
            name="Updated Trading Card Game Assistant",
            instructions="Updated instructions for trigger parsing...",
            tools=old_agent.tools,
            output_type=old_agent.output_type
        )
        
        agent_registry.register_agent('trigger_parser', new_trigger_agent)
        print("Successfully replaced trigger_parser agent")
    
    print(f"Agent count after: {len(agent_registry)}")


def demonstrate_configuration_management():
    """Demonstrate how AgentRegistry helps with configuration management"""
    print("\n=== Configuration Management ===")
    
    # Get all agents and their configurations
    all_agents = agent_registry.get_all_agents()
    
    for name, agent in all_agents.items():
        print(f"\nAgent: {name}")
        print(f"  Name: {agent.name}")
        print(f"  Tools count: {len(agent.tools) if hasattr(agent, 'tools') else 0}")
        print(f"  Has output type: {hasattr(agent, 'output_type')}")
        print(f"  Has handoffs: {len(agent.handoffs) if hasattr(agent, 'handoffs') else 0}")


async def main():
    """Main function demonstrating the integration"""
    print("AgentRegistry Integration Example")
    print("=" * 50)
    
    # Create and register agents
    create_and_register_agents()
    
    # Demonstrate benefits
    await demonstrate_registry_benefits()
    demonstrate_configuration_management()
    
    # Test the refactored function
    print("\n=== Testing Refactored Function ===")
    try:
        result = await generate_ability_with_registry("On reveal: give the top card of your deck +2 power.")
        print("Successfully generated ability using registry!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Integration example completed!")


if __name__ == "__main__":
    asyncio.run(main()) 