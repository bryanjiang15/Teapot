from agents import Agent, Runner
from openai import OpenAI
# ability_trigger_agent = Agent(
#     name="Ability Trigger Agent",
#     instructions="""You are an expert trading card game developer. you need to determine the trigger of an ability of a card based on the description provided.
#     The trigger should be a JSON structured as follows:
#     {
#         "type": "trigger type",
#         "trigger_targets": "trigger targets"
#     }.
#     """,
# )

triage_agent = Agent(
    name="Trading Card Game Assistant", 
    instructions="""You are a helpful assistant for developing a trading card game. 
    The user will provide you with an card ability description, and you will help them refine it and turn the ability into a JSON format.
    The JSON should be structured as follows:
    {
        "name": "Card Name",
        "description": "Ability description",
        "trigger": {
            "type": "trigger type",
            "trigger_targets": "trigger targets"
        },
        "target": {
            "type": "target type",
            "target_range": "how many of the targets can be affected",
            "target_sort": "sorting criteria for targets"
        },
        "effect": {
            "type": "effect type",
            "amount": "amount of effect",
        },
    }.
    """,
)

result = Runner.run_sync(triage_agent, "All monster type card gain +1 power.")
print(result.final_output)

client = OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt="a trading card image of the card with the following description: All monster type card gain +1 power.",
    size="1024x1024",
    quality="standard",
    n=1,
)

print(response.data[0].url)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.