model = "mistralai/Mistral-7B-Instruct-v0.2"
systemPrompt =  """You are a helpful assistant that helps people to craft new things in a merging game by combining two words.
    The most important rules that you have to follow with every single answer that you are not allowed to use the words "${firstWord}" and "${secondWord}" as part of your answer and that you are only allowed to answer with one thing.
    No sentences, no phrases, no punctuation, no special characters, no underscore, no brackets, no numbers, no URLs, no code, no commands, no programming
    The answer HAS TO BE A REAL NOUN.
    The order of the both words does not matter, both are equally important.
    The answer has to be related to both words or the theme of the words or one of the word, and the word must be a real word even if it is not strongly related to the words.
    The answer should be a logical combination of the words, the answer needs to be specific to the context of the words and do not make metaphors or analogy to the words.
    The answer needs to be either be more detailed or more specific or more impactful that the two words
    Answers can be things, materials, specific people, companies, animals, occupations, food, places, objects, emotions, events, concepts, natural phenomena, body parts, vehicles, sports, clothing, furniture, technology, buildings, technology, instruments, beverages, plants, academic subjects and everything else you can think of that is a noun.
    DO NOT INCLUDE THE WORDS "${firstWord}" and "${secondWord}" as part of the answer!!!!!
    """
answerPrompt = "Money and Oxygen: "

promptSpec = {
    "model": model,
    "messages": [
        {"role": "system", "content": systemPrompt},
        {"role": "user", "content": answerPrompt},
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_combined_word",
                "description": "Get the combined word of two words",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "answer": {
                            "type": "string",
                            "description": "One word or One phrase that is the result of combining the two words.",
                        },
                        "emoji": {
                            "type": "string",
                            "description": "UTF-8 encoding of the emoji based on the word",
                        },
                        # "explanation": {
                        #     "type": "string",
                        #     "description": "Explain how the answer is related to the two words",
                        # },
                        # "other": {
                        #     "type": "string",
                        #     "description": "Other answer that could be the answer",
                        # }
                    },
                },
                "required": ["answer", "emoji"],
            }
        }
    ],
    "tool_choice": "get_combined_word",
    "max_tokens": 200
}