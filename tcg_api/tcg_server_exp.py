import json
import asyncio
from agents import Agent, Runner, function_tool, FunctionTool, trace, ItemHelpers, AgentOutputSchema
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from openai import OpenAI
from abilityData import *
from abilityDefinitions import *
from typing_extensions import TypedDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@function_tool  
async def trigger_schema_tool(trigger_type: TriggerType, trigger_target_data: TargetData) -> AbilityTrigger:
    """Build an AbilityTrigger Object and check its validity.

    Args:
        trigger_type (TriggerType): The type of trigger.
        trigger_target_data (TargetData): Data specifying what target can cause the trigger to activate.
    
    """
    return AbilityTrigger(
        trigger_type=trigger_type,
        trigger_target_data=trigger_target_data 
    )

@function_tool
async def effect_schema_tool(effect_type: EffectType, amount: AmountData) -> AbilityEffect:
    """Build an AbilityEffect Object and check its validity.

    Args:
        effect_type (str): The type of effect.
        amount (AmountData): The amount of the effect.
    
    """
    return AbilityEffect(
        effect_type=effect_type,
        amount=amount
    )

@function_tool
async def target_schema_tool(target_data: TargetData) -> TargetData:
    """Build an AbilityTarget Object and check its validity.

    Args:
        target_data (TargetData): Data specifying the target of the ability.
    
    """
    return target_data

@function_tool
async def requirement_schema_tool(requirement_data: RequirementData, requirement_target: TargetData) -> AbilityRequirement:
    """Build an AbilityRequirement Object and check its validity.

    Args:
        requirement_data (RequirementData): Data specifying the requirement of the ability.
        requirement_target (TargetData): Data specifying the target that needs to pass the requirement.
    
    """
    return AbilityRequirement(
        requirement=requirement_data,
        target=requirement_target
    )

# @function_tool
# async def ability_amount_Schema_tool(amount_type: AbilityAmountType, constant_value: int, target_property: RequirementType, target: TargetData) -> dict:
#     if amount_type == AbilityAmountType.CONSTANT:
#         BaseAmountData = BaseAmountData(
#             amount_type=amount_type,
#             constant_value=constant_value
#         )
#         return BaseAmountData.to_dict()

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


triage_agent = Agent(
    name="Trading Card Game Assistant", 
    instructions="""You are a helpful assistant for developing a trading card game. 
    The user will provide you with an card ability description, and you will identify the ability and separate the ability into separate simpler abilities if needed.
    Each ability should have one effect.
    If the ability only has one effect, return the ability as a single string.
    Make sure to include the trigger, target, and effect of the ability.
    Output a list of strings describing the abilities.
    """,
)

prompt_enhance_agent = Agent(
    name="Trading Card Game Assistant",
    instructions="""You are a helpful assistant for developing a trading card game.
    The user will provide you with an card ability description, and you will identify the ability and improve the ability description to be more specific and clear.
    Include details about the trigger, target, and effect of the ability.
    The trigger should specify the event that causes the ability to activate and what targets can trigger the ability.
    The target should specify the target that the ability is applied to.
    The effect should specify the action that the ability performs and the amount of the effect.
    Output the improved ability description in 50 words or less.
    """,
)

result_examination_agent = Agent(
    name="Trading Card Game Assistant",
    instructions="""You are a helpful assistant for developing a trading card game.
    The user will provide you with an card ability description, and a json object that describe the ability.
    You will check if the json object's description matches the ability description.
    Provide a detailed reasoning for the ability description of the trigger, target, and effect.
    """,
)
# for tool in requirement_agent.tools:
#     if isinstance(tool, FunctionTool):
#         print(tool.name)
#         print(tool.description)
#         print(json.dumps(tool.params_json_schema, indent=2))
#         print()

async def check_amount_data(agent_result_type: str, agent_result: dict) -> list[str]:
    """Check if an agent result contains amount data that needs further processing.
        If the amount type is TARGET_VALUE or FOR_EACH_TARGET, the amount data needs further processing.
    Args:
        agent_result (dict): The agent result to check
        
    Returns:
        list[str]: List of amount target descriptions that need processing, empty if none found
    """
    amount_queries = []
    
    # Check trigger target data
    if agent_result_type == "trigger" and "triggerSource" in agent_result:
        trigger_data = agent_result["triggerSource"]
        if (trigger_data.get("targetRequirements", {}).get("requirementAmount", {}).get("amountType") 
            in [AbilityAmountType.TARGET_VALUE, AbilityAmountType.FOR_EACH_TARGET]):
            amount_queries.append(trigger_data["targetRequirements"]["requirementAmount"]["multiplierCondition"])
    
    # Check effect amount
    if agent_result_type == "effect":
        if agent_result["amount"].get("amountType") in [AbilityAmountType.TARGET_VALUE, AbilityAmountType.FOR_EACH_TARGET]:
            amount_queries.append(agent_result["amount"]["multiplierCondition"])
    
    # Check target requirements
    if agent_result_type == "target":
        if (agent_result["targetRequirements"].get("requirementAmount", {}).get("amountType") 
            in [AbilityAmountType.TARGET_VALUE, AbilityAmountType.FOR_EACH_TARGET]):
            amount_queries.append(agent_result["targetRequirements"]["requirementAmount"]["multiplierCondition"])
    
    return amount_queries

async def process_amount_queries(amount_queries: list[str], depth: int = 0) -> dict[str, dict]:
    """Process amount queries recursively, up to a maximum depth of 2.
    
    Args:
        amount_queries (list[str]): List of amount queries to process
        depth (int): Current recursion depth
        
    Returns:
        dict[str, dict]: Dictionary mapping original queries to their processed results
    """
    if depth >= 2 or not amount_queries:
        return {}
    
    # Process current level of amount queries
    amount_res = await asyncio.gather(
        *[Runner.run(target_agent, query) for query in amount_queries]
    )
    
    # Create mapping of queries to their results
    processed_results = {query: res.final_output for query, res in zip(amount_queries, amount_res)}
    
    # Collect results for debugging
    # for i, amount_query in enumerate(amount_res):
    #     print(f"Amount query depth {depth}, query {i}: {amount_query.final_output}")
    
    # Check for nested amount data in the results
    nested_queries = []
    query_to_parent = {}  # Map nested queries to their parent queries
    
    for query, result in zip(amount_queries, amount_res):
        nested = await check_amount_data("target", result.final_output)
        nested_queries.extend(nested)
        # Map each nested query to its parent query
        for nested_query in nested:
            query_to_parent[nested_query] = query
    
    # Recursively process nested queries
    if nested_queries:
        nested_results = await process_amount_queries(nested_queries, depth + 1)
        # Update parent results with nested results
        for query, result in processed_results.items():
            await update_processed_amounts("target", result, nested_results)
    
    return processed_results

async def update_processed_amounts(output_type: str, output: dict, processed_results: dict[str, dict]) -> None:
    """Update the output with processed amount results.
    
    Args:
        output_type (str): Type of the output ("trigger", "effect", or "target")
        output (dict): The output to update
        processed_results (dict[str, dict]): Dictionary of processed results
    """
    if output_type == "trigger" and "triggerSource" in output:
        trigger_data = output["triggerSource"][0]
        if (trigger_data.get("targetRequirements", {}).get("requirementAmount", {}).get("amountType") 
            in [AbilityAmountType.TARGET_VALUE, AbilityAmountType.FOR_EACH_TARGET]):
            query = trigger_data["targetRequirements"]["requirementAmount"]["multiplierCondition"]
            if query in processed_results:
                trigger_data["targetRequirements"]["requirementAmount"]["value"] = processed_results[query]
    
    elif output_type == "effect" and "amount" in output:
        if output["amount"].get("amountType") in [AbilityAmountType.TARGET_VALUE, AbilityAmountType.FOR_EACH_TARGET]:
            query = output["amount"]["multiplierCondition"]
            if query in processed_results:
                output["amount"]["value"] = processed_results[query]
    
    elif output_type == "target" and "targetRequirements" in output:
        if (output["targetRequirements"].get("requirementAmount", {}).get("amountType") 
            in [AbilityAmountType.TARGET_VALUE, AbilityAmountType.FOR_EACH_TARGET]):
            query = output["targetRequirements"]["requirementAmount"]["multiplierCondition"]
            if query in processed_results:
                output["targetRequirements"]["requirementAmount"]["value"] = processed_results[query]

async def Generate_Ability(ability_description: str):

    # with trace("Ability Enhancement"):
    #     enhanced_ability_description = await Runner.run(prompt_enhance_agent, ability_description)
    #     print(enhanced_ability_description.final_output)

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
        processed_results = await process_amount_queries(initial_queries)
        
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
    
    # with trace("Result Examination"):
    #     result_examination_res = await Runner.run(result_examination_agent, f"ability description: {ability_description}\nability json: {result}")
    #     print(result_examination_res.final_output)

# client = OpenAI()

# response = client.images.generate(
#     model="dall-e-3",
#     prompt="a trading card image of the card with the following description: All monster type card gain +1 power.",
#     size="1024x1024",
#     quality="standard",
#     n=1,
# )

# print(response.data[0].url)

# You are a helpful assistant for developing a trading card game. 
#     The user will provide you with an card ability description, and you will identify the trigger of the ability and turn the trigger into a JSON format.
#     The JSON should be structured as follows:
#     {
#         "name": "Card Name",
#         "description": "Ability description",
#         "trigger": {
#             "type": "trigger type",
#             "trigger_targets": "trigger targets"
#         },
#         "target": {
#             "type": "target type",
#             "target_range": "how many of the targets can be affected",
#             "target_sort": "sorting criteria for targets"
#         },
#         "effect": {
#             "type": "effect type",
#             "amount": "amount of effect",
#         },
#     }.

if __name__ == "__main__":
    asyncio.run(Generate_Ability("On reveal: give the top card of your deck +2 power."))