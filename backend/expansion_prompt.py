model = "mistralai/Mistral-7B-Instruct-v0.2"
upgrade_systemPrompt =  """You are a helpful assistant that return a list of more specific answer than the word provided.
    The answers HAS TO BE real nouns/objects that is related to the word or the theme of the word and more specific.
    No sentences, no phrases, no punctuation, no special characters, no underscore, no brackets, no numbers, no URLs, no code, no commands, no programming
    If the word is an animal, the answer should be a specific species of the animal.
    If the word is a place, the answer should be a specific location related.
    If the word is a object, the answer should be a specific person/object/event that is related to the word.
    Answers can be things, materials, specific people, companies, animals, occupations, food, locations, scientific terms, historical events, concepts, natural phenomena, body parts, vehicles, sports, technology, buildings, instruments, academic subjects and everything else you can think of that is a noun.
    """
upgrade_answerPrompt = "Movie: "

upgrade_promptSpec = {
    "model": model,
    "messages": [
        {"role": "system", "content": upgrade_systemPrompt},
        {"role": "user", "content": upgrade_answerPrompt},
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_specific_word",
                "description": "Get a list of more specific words based on the word",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "answers": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                    },
                },
                "required": ["answers"],
            }
        }
    ],
    "tool_choice": "get_specific_word",
    "max_tokens": 100
}