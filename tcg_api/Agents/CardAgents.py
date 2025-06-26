from Agents.agent_registry import agent_registry
from agents import Agent, function_tool, AgentOutputSchema
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from abilityData import *
from abilityDefinitions import *   

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


ability_decomposition_agent = Agent(
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

art_generation_agent = Agent(
    name="Trading Card Game Assistant",
    instructions="""You are a helpful assistant for developing a trading card game.
    The user will provide you with an card ability description, and you will generate an art for the card.
    Output the art in a JSON object.
    """,
    model="gpt-4o-mini",
)

agents_to_register = {
    "trigger_agent": trigger_agent,
    "effect_agent": effect_agent,
    "target_agent": target_agent,
    "requirement_agent": requirement_agent,
    "ability_decomposition_agent": ability_decomposition_agent,
    "prompt_enhance_agent": prompt_enhance_agent,
    "result_examination_agent": result_examination_agent,
    "art_generation_agent": art_generation_agent,
}

def register_agents():
    agent_registry.register_multiple_agents(agents_to_register)
