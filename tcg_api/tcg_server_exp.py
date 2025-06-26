from dataclasses import dataclass, asdict
import asyncio
from abilityDefinitions import AbilityTrigger, AbilityEffect, TargetData
from agents import Agent, Runner, function_tool, FunctionTool, trace, ItemHelpers, AgentOutputSchema
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from openai import OpenAI
from abilityData import *
from abilityDefinitions import *
from typing_extensions import TypedDict
from dotenv import load_dotenv
from AmountProcessors.amount_processing import AmountProcessor
from Agents.agent_registry import agent_registry
from Agents.CardAgents import register_agents, trigger_schema_tool, effect_schema_tool, target_schema_tool
# Load environment variables from .env file
load_dotenv()

register_agents()
amount_processor = AmountProcessor()

async def generate_art(card_description: str):
    client = OpenAI()
    prompt = f"""Create a vibrant, stylized illustration in the style of a marvel comic cover. Depict: {card_description}. 
    Focus on a single creature in a dynamic pose, with an expressive face and action-ready posture. 
    Use a clean digital art style with bold outlines, smooth gradients. 
    Include a simple background. 
    The artwork should be suitable for use on a marvel comic cover.
    """

    result = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1792"
    )

    return result.data[0].url
# for tool in requirement_agent.tools:
#     if isinstance(tool, FunctionTool):
#         print(tool.name)
#         print(tool.description)
#         print(json.dumps(tool.params_json_schema, indent=2))
#         print()

async def Generate_Ability(ability_description: str, card_description: str):

    # with trace("Ability Enhancement"):
    #     enhanced_ability_description = await Runner.run(prompt_enhance_agent, ability_description)
    #     print(enhanced_ability_description.final_output)

    trigger_agent = agent_registry.get_agent('trigger_agent')
    effect_agent = agent_registry.get_agent('effect_agent')
    target_agent = agent_registry.get_agent('target_agent')

    result = None
    with trace("Ability Configuration"):
        Trigger_res, Effect_res, Target_res, art_url = await asyncio.gather(
            Runner.run(trigger_agent, ability_description),
            Runner.run(effect_agent, ability_description),
            Runner.run(target_agent, ability_description),
            generate_art(card_description)
        )

        outputs = {
            "trigger": Trigger_res.final_output,  # type: AbilityTrigger
            "effect": Effect_res.final_output,    # type: AbilityEffect
            "target": Target_res.final_output,    # type: TargetData
        }

        # Collect initial amount queries
        initial_queries = []
        for output in outputs.values():
            initial_queries.extend(amount_processor.check_amount_data(output))
        
        # Process amount queries recursively
        processed_results = await amount_processor.process_amount_data(initial_queries)
        
        # Update outputs with processed results
        for output in outputs.values():
            await amount_processor.update_processed_amounts(output, processed_results)
    
        result = AbilityResponse(
            AbilityDefinition=AbilityDefinition(
                triggerDefinition=outputs["trigger"],
                targetDefinition=[outputs["target"]],
                effect=outputs["effect"].effectType,
                amount=outputs["effect"].amount,
            ),
            CardArtUrl=art_url,
        )

        print(result)
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
    card_description = "A techno-organic creature that scans the battlefield."
    asyncio.run(Generate_Ability("On reveal: give the top card of your deck +2 power.", card_description))