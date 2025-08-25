import asyncio
from openai import OpenAI
from abilityGenerationPipeline import AbilityGenerationPipeline
from Agents.CardAgents import register_agents

async def generate_art(card_description: str):
    client = OpenAI()
    prompt = f"""Create a detailed, high-fantasy illustration in the style of Magic: The Gathering trading cards. 
    The scene features: {card_description}. Use dramatic lighting, rich colors, and painterly textures. 
    The composition should be dynamic and focused on the main subject, with a complementary background. 
    The mood should match the description. Do not include any text or borders—only the illustration.
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
register_agents()

async def Generate_Ability(ability_description: str, card_description: str):
    """
    Generate a complete ability using the AbilityGenerationPipeline.
    
    Args:
        ability_description (str): Description of the ability to generate
        card_description (str): Description of the card for art generation
        
    Returns:
        AbilityResponse: Complete ability response with definition and art URL
    """
    pipeline = AbilityGenerationPipeline()
    return await pipeline.generate_ability(ability_description, card_description)
    
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
    card_description = "Human torch from marvel comics."
    asyncio.run(Generate_Ability("End of turn: gain +1 power. If this has 5 or more power, draw a card.", card_description))