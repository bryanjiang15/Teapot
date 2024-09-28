import LlamaAI from "llamaai";
const apiToken = 'LA-06f05dab438246fe86d4ffeccb94fd9601b15725c8334cd0ab0ea883b3c254f7';
const llamaAPI = new LlamaAI(apiToken);

let firstWord = "Maxwell's equation";
let secondWord = 'Sun';

let systemPrompt = "You are a helpful assistant that helps people to craft new things by combining two words." + 
"The most important rules that you have to follow with every single answer that you are not allowed to use the words" +
firstWord + " and " + secondWord + " as part of your answer and that you are only allowed to answer with one thing." +
"DO NOT INCLUDE THE WORDS " + firstWord + " and " + secondWord + " as part of the answer!!!!! The words {firstWord} and {secondWord} may NOT be part of the answer." +
"No sentences, no phrases, no multiple words, no punctuation, no special characters, no numbers, no emojis, no URLs, no code, no commands, no programming." +
"The answer has to be a noun." +
"The order of the both words does not matter, both are equally important." +
"The answer has to be related to both words and the context of the words." +
"The answer can either be a combination of the words or the role of one word in relation to the other." +
"Answers can be things, materials, people, companies, animals, occupations, food, places, objects, emotions, events, concepts, natural phenomena, body parts, vehicles, sports, clothing, furniture, technology, buildings, technology, instruments, beverages, plants, academic subjects and everything else you can think of that is a noun." +
"If the answer is not a real word or a proper noun, return NULL." +
"Reply with the result of what would happen if you combine {firstWord} and {secondWord}." +
"The answer has to be related to both words and the context of the words and may not contain the words themselves. ";
let answerPrompt = firstWord + " and " + secondWord;

// Build the Request
const apiRequestJson = {
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
    "stream": false,
    "function_call": "get_combined_word",
   };
 
   // Execute the Request
    llamaAPI.run(apiRequestJson)
      .then(response => {
        // Process response
        console.log(response.choices[0]);
      })
      .catch(error => {
        // Handle errors
      });
 