import { HfInference } from "@huggingface/inference";
import dotenv from "dotenv";

dotenv.config();

const HF_ACCESS_TOKEN = process.env.HF_ACCESS_TOKEN

const inference = new HfInference(HF_ACCESS_TOKEN);

const model = "mistralai/Mistral-7B-Instruct-v0.3"

let firstWord = "water";
let secondWord = "fire";

let systemPrompt = "You are a helpful assistant that helps people to craft new things in a merging game by combining two words." + 
    "The most important rules that you have to follow with every single answer that you are not allowed to use the words" +
    firstWord + " and " + secondWord + " as part of your answer and that you are only allowed to answer with one thing." +
    "DO NOT INCLUDE THE WORDS " + firstWord + " and " + secondWord + " as part of the answer!!!!! The words " + firstWord + " and " + secondWord + " may NOT be part of the answer." +
    "No sentences, no phrases, no multiple words, no punctuation, no special characters, no numbers, no emojis, no URLs, no code, no commands, no programming." +
    "The answer has to be a noun and a actual word that exist." +
    // "The order of the both words does not matter, both are equally important." +
    "The answer has to be related to both words and the theme of the words." +
    "The answer can either be a combination of the words or how one word is used in the context of the other word." +
    "The answer should be a logical combination of the words, the answer needs to be specific to the context of the words and do not make metaphors or analogy to the words." +
    "The answer needs to be either be more detailed or more specific or more impactful that the two words" +
    "Answers can be things, materials, specific people, companies, animals, occupations, food, places, objects, emotions, events, concepts, natural phenomena, body parts, vehicles, sports, clothing, furniture, technology, buildings, technology, instruments, beverages, plants, academic subjects and everything else you can think of that is a noun." +
    //"If you cannot come up with a answer, that follows the rules, instead output a word that is more specific to either" + firstWord + "or " + secondWord + "." +
    "If the answer is not a real word or a proper noun, return NULL." +
    "Reply with the result of what would happen if you combine" + firstWord + " and " + secondWord + "." +
    "The answer has to be related to both words and the context of the words and may not contain the words themselves. ";
    let answerPrompt = firstWord + " and " + secondWord;

const result = await inference.chatCompletion({
    model: model,
    messages: [
        {"role": "system", "content": systemPrompt},
        {"role": "user", "content": answerPrompt},
    ],
    tools: [
        {
            type: "function",
            function: {
                name: "get_combined_word",
                description: "Get the combined word of two words",
                parameters: {
                    type: "object",
                    properties: {
                        answer: {
                            type: "string",
                            description: "One word or One phrase that is the result of combining the two words.",
                        },
                        explanation: {
                            type: "string",
                            description: "Explain how the answer is related to the two words",
                        },
                        // "other": {
                        //     "type": "string",
                        //     "description": "Other answer that could be the answer",
                        // }
                    },
                },
                required: ["answer"],
            }
        }
    ],
    tool_choice: "get_combined_word"
})

console.log(result.choices[0].message.tool_calls[0])

let albumSystemPrompt = "You are designing a trading card based on a given word." +
    "Each card must have a name, category, emoji, and health.";
    "The card's name is the given word." +
    "The card's category is the broader type of object the word represents, such as animals, math equations, famous people, etc." +
    "The emoji uses UTF-8 encoding generate this based on the word." +
    "Health is a number from 10 to 200, based on the word's complexity, size, or importance." +
    "YOU MUST Provide the card's name, rarity, category, emoji, health. Do not provide any other information or text explaning the answer.";
    
let albumAnswerPrompt = "chainsaw";
const card_api_request_json = {
    model: model,
    messages: [
        {"role": "system", "content": albumSystemPrompt},
        {"role": "user", "content": albumAnswerPrompt},
    ],
    tools: [
        {
            type: "function",
            function: {
                name: "create_card",
                description: "Get the design of the card based on the word: "+ albumAnswerPrompt,
                parameters: {
                    type: "object",
                    properties: {
                        category: {
                            type: "string",
                            description: "The category of the card based on the input word",
                        },
                        emoji: {
                            type: "string",
                            description: "UTF-8 encoding of the emoji based on the input word",
                        },
                        health: {
                            type: "integer",
                            description: "The health of the card",
                        },
                    },
                },
                required: ["category", "emoji", "health"],
            }
        }
    ],
    tool_choice: "create_card"
}



//setId(id + 1);

let card_response = await inference.chatCompletion(card_api_request_json);
console.log(card_response.choices[0].message.tool_calls[0]);
//console.log(card_response.choices[0].message)