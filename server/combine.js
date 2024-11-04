import LlamaAI from "llamaai";
import {LLAMA_SECRET_KEY} from "./env.js";
import Card from './components/card' 
const apiToken = LLAMA_SECRET_KEY;

async function get_combined_word(firstWord, secondWord, id, setId, setCards, cards) {
    const llamaAPI = new LlamaAI(apiToken);
    let systemPrompt = "You are a helpful assistant that helps people to craft new things in a merging game by combining two words." + 
    "The most important rules that you have to follow with every single answer that you are not allowed to use the words" +
    firstWord + " and " + secondWord + " as part of your answer and that you are only allowed to answer with one thing." +
    "DO NOT INCLUDE THE WORDS " + firstWord + " and " + secondWord + " as part of the answer!!!!! The words " + firstWord + " and " + secondWord + " may NOT be part of the answer." +
    "No sentences, no phrases, no multiple words, no punctuation, no special characters, no numbers, no emojis, no URLs, no code, no commands, no programming." +
    "The answer has to be a noun." +
    "The order of the both words does not matter, both are equally important." +
    "The answer has to be related to both words and the theme of the words." +
    "The answer can either be a combination of the words or how one word is used in the context of the other word." +
    "The answer should be a logical combination of the words, the answer needs to be specific to the context of the words and do not make metaphors or analogy to the words." +
    "The answer needs to be either be more detailed or more specific or more impactful that the two words" +
    "Answers can be things, materials, specific people, companies, animals, occupations, food, places, objects, emotions, events, concepts, natural phenomena, body parts, vehicles, sports, clothing, furniture, technology, buildings, technology, instruments, beverages, plants, academic subjects and everything else you can think of that is a noun." +
    //"If you cannot come up with a answer, that follows the rules, instead output a word that is more specific to either" + firstWord + "and " + secondWord + "." +
    "If the answer is not a real word or a proper noun, return NULL." +
    "Reply with the result of what would happen if you combine" + firstWord + " and " + secondWord + "." +
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
                        // "other": {
                        //     "type": "string",
                        //     "description": "Other answer that could be the answer",
                        // }
                    },
                },
                "required": ["answer"],
            }
        ],
        "stream": false,
        "function_call": "get_combined_word",
    };
    
    let ai_response = null;
    // Execute the Request
    await llamaAPI.run(apiRequestJson)
        .then(response => {
        // Process response
        ai_response = response;
        console.log(response.choices[0].message);
        })
        .catch(error => {
        // Handle errors
        });
    
    let combined_word = ai_response.choices[0].message.function_call.arguments.answer;
    // let albumSystemPrompt = "You are a helpful assistant that helps people design new cards in a trading card game based on an input word." +
    // "Every card must include a name, emoji, health, rarity, and power." +
    // "The name of the card is the word inputed by the user." +
    // "The emoji of the card is based on the word inputed by the user using UTF-8 encoding." +
    // "The health of the card is based on the complexity of the word, a number between 10-200." +
    // "The rarity is based on the name of the card. The rarity can be common, rare, epic, or legendary." +
    // "The rarity should be based on how important the word is to its specific theme or category." +
    // "The power of the card is based on the rarity of the card. The power should range from 10 to 200. The rarer the card, the more powerful it is." +
    // "common rarity: 10-70 power, rare rarity: 50-120 power, epic rarity: 80-150 power, legendary rarity: 131-200 power." +
    // "The power can be randomized within the range of the rarity, and the power can als be based on the size of the object described by the word, the importance of the word in its category, the danger of the object described by the word." +
    // "Reply with the name, emoji, health, rarity, and power of the card based on the input word.";
    let albumSystemPrompt = "You are designing a trading card based on a given word." +
    "Each card must have a name, emoji, health, and power." +
    "The card's name is the given word." +
    "The emoji uses UTF-8 encoding generate this based on the word." +
    "Health is a number from 10 to 200, based on the word's complexity." +
    "Power ranges from 10 to 200, based on the word's importance in its category." +
    "YOU MUST Provide the card's name, emoji, health, and power.";
    
    let albumAnswerPrompt = combined_word
    const card_api_request_json = {
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
                            "description": "The name of the card based on the input word",
                        },
                        "emoji": {
                            "type": "string",
                            "description": "UTF-8 encoding of the emoji based on the input word",
                        },
                        "health": {
                            "type": "integer",
                            "description": "The health of the card",
                        },
                        "power": {
                            "type": "integer",
                            "description": "The power of the card",
                        }
                    },
                },
                "required": ["name", "health", "emoji","power"],
            }
        ],
        "stream": false,
        "function_call": "get_card",
    }

    setId(id + 1);

    let card_response = null;
    await llamaAPI.run(card_api_request_json)
        .then(response => {
        // Process response
        card_response = response;
        console.log(response);
        })
        .catch(error => {
        // Handle errors
        });
    if (card_response == null) {
        console.log("Card response is null");
        return null;
    }
    let combined_card = {
        "name": card_response.choices[0].message.function_call.arguments.name,
        "rarity": card_response.choices[0].message.function_call.arguments.rarity,
        "power": card_response.choices[0].message.function_call.arguments.power,
        "emoji": card_response.choices[0].message.function_call.arguments.emoji,
        "health": card_response.choices[0].message.function_call.arguments.health
    }
    
    console.log(combined_card);


    let card = {
        "id": id+1,
        "health": combined_card.health,
        "power": combined_card.power,
        "name": combined_card.name,
        "emoticon": combined_card.emoji
    };

    // let card = {
    //     "id": id,
    //     "health": 10,
    //     "power": 10,
    //     "name": combined_word,
    //     "emoticon": "🃏"
    // }

    cards.unshift(card);
    setCards([...cards]);
    console.log(cards);

    return;

}