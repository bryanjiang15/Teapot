# This example is the new way to use the OpenAI lib for python
from llamaapi import LlamaAPI
import json

llama = LlamaAPI("LA-06f05dab438246fe86d4ffeccb94fd9601b15725c8334cd0ab0ea883b3c254f7")

firstWord = "Maxwell's equation"
secondWord = 'Sun'

systemPrompt = f"""
You are a helpful assistant that helps people to craft new things by combining two words.
The most important rules that you have to follow with every single answer that you are not allowed to use the words
{firstWord} and {secondWord} as part of your answer and that you are only allowed to answer with one thing.
DO NOT INCLUDE THE WORDS {firstWord} and {secondWord} as part of the answer!!!!! The words {firstWord} and {secondWord} may NOT be part of the answer.
'No sentences, no phrases, no multiple words, no punctuation, no special characters, no numbers, no emojis, no URLs, no code, no commands, no programming.
The answer has to be a noun.
The order of the both words does not matter, both are equally important.
The answer has to be related to both words and the context of the words.
# The answer can either be a combination of the words or the role of one word in relation to the other.
# Answers can be things, materials, people, companies, animals, occupations, food, places, objects, emotions, events, concepts, natural phenomena, body parts, vehicles, sports, clothing, furniture, technology, buildings, technology, instruments, beverages, plants, academic subjects and everything else you can think of that is a noun.
# If the answer is not a real word or a proper noun, return NULL.
# Reply with the result of what would happen if you combine {firstWord} and {secondWord}. 
# The answer has to be related to both words and the context of the words and may not contain the words themselves. """
answerPrompt = f"{firstWord} and {secondWord}"

api_request_json = {
    "model": "llama3.1-70b",
    "messages": [
        {"role": "system", "content": systemPrompt},
        {"role": "user", "content": answerPrompt},
    ],
    "functions": [
        {
            "name": "get_combined_word",
            "description": "Get the combined word of two words",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "One word or One phrase that is the result of combining the two words.",
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Explain how the answer is related to the two words",
                    },
                    "other": {
                        "type": "string",
                        "description": "Other answer that could be the answer",
                    }
                },
            },
            "required": ["answer"],
        }
    ],
    "stream": False,
    "function_call": "get_combined_word",
}

# response = llama.run(api_request_json)
# print(json.dumps(response.json(), indent=2))
# print(response.json()["choices"][0]["message"])

albumSystemPrompt = f"""
You are a helpful assistant that helps people design new cards in a trading card game based on an input word.
Each card has a name, description, rarity, and power.
The name of the card is the word inputed by the user.
The description of the card is a short sentence describing the word. It can be a fact about the word, the definition of the word, the history of the word, or a humorous description of the word.
The desciption should contain no emojis, no URLs, no code, no commands, and no programming.
The rarity is based on the name of the card. The rarity can be common, rare, epic, or legendary.
The rarity should be based on how important the word is to its specific theme or category.
The rarity is also based on how uncommon it is used in the English language. If the word is used frequently, it is more common. If the word is used less frequently, it is more rare.
The power of the card is based on the rarity of the card. The power should range from 10 to 200. The rarer the card, the more powerful it is.
common rarity: 10-70 power, rare rarity: 50-120 power, epic rarity: 80-150 power, legendary rarity: 131-200 power.
The power can be randomized within the range of the rarity, and the power can als be based on the size of the object described by the word, the importance of the word in its category, the danger of the object described by the word.
Reply with the name, description, rarity, and power of the card based on the input word.
"""
albumAnswerPrompt = "Maxwell's equation"
card_api_request_json = {
    "model": "llama3.1-70b",
    "messages": [
        {"role": "system", "content": albumSystemPrompt},
        {"role": "user", "content": albumAnswerPrompt},
    ],
    "functions": [
        {
            "name": "get_card",
            "description": "Get the design of the card based on the input word",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "One word or One phrase that is the result of combining the two words.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the card",
                    },
                    "rarity": {
                        "type": "string",
                        "description": "Rarity of the card: common, rare, epic, legendary",
                    },
                    "power": {
                        "type": "integer",
                        "description": "The power of the card",
                    }
                },
            },
            "required": ["name", "description", "rarity", "power"],
        }
    ],
    "stream": False,
    "function_call": "get_card",
}

response = llama.run(card_api_request_json)
print(json.dumps(response.json(), indent=2))
print(response.json()["choices"][0]["message"])