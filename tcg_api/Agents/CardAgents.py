from Agents.agent_registry import agent_registry
from agents import Agent, function_tool, AgentOutputSchema
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from abilityData import *
from abilityDefinitions import *   
from typing import List
from SnapComponents.SnapComponent import SnapComponent

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
    name="Trigger Agent", 
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a helpful assistant for developing a trading card game. 
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
    name="Create Card Effect Agent",
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
    name="Effect Agent", 
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a helpful assistant for developing a trading card game. 
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
    name="Target Agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a helpful assistant for developing a trading card game.
    The user will provide you with an card ability description, and you will identify the target of the ability that will be affected.
    The target is the target that the effect is applied to, NOT the target that causes the ability to activate or the target that determines the effect of the ability.
    The target should be determined by the effect type. Call the get_valid_target_types tool to get a list of valid target types for the effect type and select one.
    Output a JSON object of the target schema.
    """,
    tools=[
        get_valid_effect_target_types
    ],
    output_type=AgentOutputSchema(TargetData)
)

requirement_agent = Agent(
    name="Requirement Agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a helpful assistant for developing a trading card game.
    The user will provide you with an card ability description, and you will identify the abilities' requirement to activate.
    The requirement is the condition that must be met for the ability to activate when the ability is triggered, the requirement is NOT the trigger.
    
    The requirement should also include the target that needs to pass the requirement. The target does NOT equal the target the effect is applied to, but it can be.
    If the ability has no requirement, return an empty JSON object.
    Output a JSON object of the requirement schema.
    """,
    tools=[
        requirement_schema_tool,
    ],
    output_type=AgentOutputSchema(AbilityRequirement)
)


ability_decomposition_agent = Agent(
    name="Ability Decomposition Agent", 
    instructions="""You are a helpful assistant for developing a trading card game. 
    The user will provide you with a card ability description, and you will decompose it into modular components for analysis and implementation.

    **Component Types:**
    1. **Trigger Component**: The event that activates the ability (must be first)
       - Event type (OnReveal, OnPlay, OnDeath, etc.)
       - Trigger source (what can cause the trigger)
       - Timing and conditions for activation
    
    2. **Action Component**: The action/effect the ability performs
       - Action type (GainPower, DrawCard, DestroyCard, etc.)
       - Amount/value of the action
       - Target of the action (what receives the action)
       - Duration and persistence of the action
    
    3. **Condition Component**: Requirements that must be met
       - If/while conditions that control ability execution
       - Target requirements (power, cost, card type, etc.)
       - Player state requirements (hand size, energy, etc.)
       - Each condition must have a corresponding end condition
    
    4. **Choice Component**: Player choices and user input
       - Choice type (If, While, Else)
       - Actions that the player must make
       - Target selection requirements (specific target or group of targets)
       - Choice options and their effects 
    
    5. **End Condition Component**: Marks the end of conditional blocks
       - Must pair with each condition component
       - Defines scope of conditional effects
    
    **Decomposition Guidelines:**
    - Identify the logical flow and dependencies
    - Separate distinct functional elements
    - Maintain chronological order where relevant
    - Include all implicit conditions and requirements
    - Consider edge cases and alternative scenarios
    
    Output a list of SnapComponent, each with a componentType and componentDescription,  describing a single component in clear, concise language (max 200 words per component).
    Use consistent terminology and be specific about targets, amounts, and conditions.
    """,
    output_type=AgentOutputSchema(List[SnapComponent])
)

prompt_enhance_agent = Agent(
    name="Prompt Enhance Agent",
    instructions="""You are a helpful assistant for developing a trading card game.
    The user will provide you with an card ability description, and you will identify the ability and improve the ability description to be more specific and clear.
    Include details about the trigger, target, and effect of the ability.
    The trigger should specify the event that causes the ability to activate and what targets can trigger the ability.
    The target should specify the target that the ability is applied to.
    The effect should specify the action that the ability performs and the amount of the effect.
    Output the improved ability description in 50 words or less.
    """,
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="""You are a helpful assistant for developing a trading card game.
    You are provided with a component from a decomposed card ability and the full ability description.
    
    Your task is to analyze the component and determine which specialized agent should process it:
    
    **Component Classification:**
    1. **Trigger Component**: Contains events like "OnReveal", "OnPlay", "End of turn", "When this card is played"
       → Handoff to trigger_agent
    
    2. **Effect Component**: Contains actions like "gain power", "draw cards", "destroy cards", "heal", "damage"
       → Handoff to effect_agent
    
    3. **Target Component**: Contains target specifications like "all cards", "this card", "opponent's cards", "your deck"
       → Handoff to target_agent
    
    4. **Requirement Component**: Contains conditions like "if you have", "while this has", "when this card has X power"
       → Handoff to requirement_agent
    
    **Analysis Process:**
    - Read the component carefully
    - Identify the primary function of the component
    - Consider the context from the full ability description
    - Route to the most appropriate agent
    - Provide clear reasoning for your choice
    
    If a component contains multiple aspects, prioritize the most dominant one or split into multiple handoffs if necessary.
    """,
    handoffs=[
        trigger_agent,
        effect_agent,
        target_agent,
        requirement_agent,
    ]
)

result_examination_agent = Agent(
    name="Result Examination Agent",
    instructions="""You are a helpful assistant for developing a trading card game.
    The user will provide you with a card ability description and a JSON object that describes the parsed ability.
    
    Your task is to thoroughly examine and validate the JSON object against the original ability description.
    
    Analyze the following components:
    1. **Trigger Analysis**: Verify the trigger type and trigger source match the ability description
    2. **Effect Analysis**: Confirm the effect type and amount data accurately represent the ability's action
    3. **Target Analysis**: Validate that the target definition correctly identifies what the effect applies to
    4. **Requirement Analysis**: Check if any activation requirements are properly captured
    5. **Overall Consistency**: Ensure all components work together logically
    
    For each component, provide:
    - Whether it matches the original description (✓ or ✗)
    - Specific reasoning for your assessment
    - Any discrepancies or missing elements
    - Suggestions for improvement if needed
    
    Output your analysis as a list of strings, with each string containing a specific finding or observation, separated by a new line.
    Be thorough but concise in your analysis.
    """,
    output_type=AgentOutputSchema(List[str])
)

art_generation_agent = Agent(
    name="Art Generation Agent",
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
    "triage_agent": triage_agent,
    "result_examination_agent": result_examination_agent,
    "art_generation_agent": art_generation_agent,
}

def register_agents():
    agent_registry.register_multiple_agents(agents_to_register)
