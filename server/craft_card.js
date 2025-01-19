import LlamaAI from "llamaai";
import {LLAMA_SECRET_KEY, OPENAI_API_KEY} from "../src/env.js";
import {db} from "./database.js";
import OpenAI from "openai";
// import { fileURLToPath } from "url";
// import path from "path";
// import { getLlama, LlamaChatSession, LlamaContext, LlamaJsonSchemaGrammar, LlamaModel } from "node-llama-cpp";
//import Card from './components/card' 
import { HfInference } from "@huggingface/inference";
import dotenv from "dotenv";

const apiToken = LLAMA_SECRET_KEY;
const openaiToken = OPENAI_API_KEY;

dotenv.config();

const HF_ACCESS_TOKEN = process.env.HF_ACCESS_TOKEN
const inference = new HfInference(HF_ACCESS_TOKEN);
const model = "mistralai/Mistral-7B-Instruct-v0.2"

async function craft_new_word_from_cache(firstWord, secondWord) {
    let cachedResult = await db.get('SELECT result, emoji FROM word_cache WHERE first_word = ? AND second_word = ?', [firstWord, secondWord]);
    if (cachedResult) {
        return cachedResult;
    }

    cachedResult = await db.get('SELECT result, emoji FROM word_cache WHERE first_word = ? AND second_word = ?', [secondWord, firstWord]);

    return cachedResult;
}

async function cacheNewWord(firstWord, secondWord, result, emoji) {
    await db.run('INSERT INTO word_cache (first_word, second_word, result, emoji) VALUES (?, ?, ?, ?)', [firstWord, secondWord, result, emoji]);
}

async function craft_new_word(firstWord, secondWord, id, setId, setCards, cards) {
    const cachedResult = await craft_new_word_from_cache(firstWord, secondWord);
    if (cachedResult) {
        return cachedResult;
    }
    const openai = new OpenAI({
        apiKey: openaiToken,
        //baseURL: "https://api.llama-api.com"
    }
    );
    const llamaAPI = new LlamaAI(apiToken);

    let systemPrompt = "You are a helpful assistant that helps people to craft new things in a merging game by combining two words." + 
    "The most important rules that you have to follow with every single answer that you are not allowed to use the words" +
    firstWord + " and " + secondWord + " as part of your answer and that you are only allowed to answer with one thing." +
    "DO NOT INCLUDE THE WORDS " + firstWord + " and " + secondWord + " or " + firstWord+secondWord+" as part of the answer!!!!!" +
    "No sentences, no phrases, no punctuation, no special characters, no underscore, no brackets, no numbers, no URLs, no code, no commands, no programming." +
    "The answer HAS TO BE A REAL WORD. The answer cannot be " + firstWord + " and " + secondWord + " joined together as one word" +
    // "The order of the both words does not matter, both are equally important." +
    "The answer has to be related to both words or the theme of the words, and the word must be a real word even if it is not strongly related to " + firstWord + " and " + secondWord + "." +
    "The answer can either be a combination of the words or how one word is used in the context of the other word." +
    "The answer should be a logical combination of the words, the answer needs to be specific to the context of the words and do not make metaphors or analogy to the words." +
    "The answer needs to be either be more detailed or more specific or more impactful that the two words" +
    "Answers can be things, materials, specific people, companies, animals, occupations, food, places, objects, emotions, events, concepts, natural phenomena, body parts, vehicles, sports, clothing, furniture, technology, buildings, technology, instruments, beverages, plants, academic subjects and everything else you can think of that is a noun." +
    //"If you cannot come up with a answer, that follows the rules, instead output a word that is more specific to either" + firstWord + "or " + secondWord + "." +
    // "If the answer is not a real word or a proper noun, return NULL." +
    "Reply with the result of what would happen if you combine" + firstWord + " and " + secondWord + "." +
    "The answer has to be related to both words and the context of the words and may not contain the words themselves. " +
    "also provide an emoji in UTF-8 encoding that represents the word.";
    let answerPrompt = firstWord + " and " + secondWord;

    // Build the Request
    const apiRequestJson = {
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
                            emoji: {
                                type: "string",
                                description: "UTF-8 encoding of the emoji based on the word",
                            },
                            // explanation: {
                            //     type: "string",
                            //     description: "Explain how the answer is related to the two words",
                            // },
                            // "other": {
                            //     "type": "string",
                            //     "description": "Other answer that could be the answer",
                            // }
                        },
                    },
                    required: ["answer", "emoji"],
                }
            }
        ],
        tool_choice: "get_combined_word",
        max_tokens: 200
    }

    let combined_word = "";
    let emoji = "";
    //error message format -> turn into json
    //{\"function\":{\"_name\":\"get_combined_word\",\"answer\":\"hillrat\",\"emoji\":\"(?:\\xD7\\x96\\xD7\\x92\\xD7\\x9D)\"}}
    const response = await inference.chatCompletion(apiRequestJson)
        .catch(error => {
            let answerIndexStart = error.message.indexOf("{");
            let answerIndexEnd = error.message.lastIndexOf("}");
            let answer = error.message.substring(answerIndexStart, answerIndexEnd+1);
            //remove escape characters
            answer = answer.replace(/\\/g, "");
            console.log(answer);
            response = JSON.parse(answer);
            
        });
    if(response.choices[0].message.tool_calls==null){
        combined_word = response.choices[0].message.content;
    }else{
        combined_word = response.choices[0].message.tool_calls[0].function.arguments.answer;
        emoji = response.choices[0].message.tool_calls[0].function.arguments.emoji;
    }
    console.log(response.choices[0].message.tool_calls[0]);
    
    //LLAMA API REQUEST
    // let ai_response = null;
    // // Execute the Request
    // await llamaAPI.run(apiRequestJson)
    //     .then(response => {
    //     // Process response
    //     ai_response = response;
        
    //     })
    //     .catch(error => {
    //     // Handle errors
    //     console.log(error);
    //     });
    //     console.log(ai_response.choices[0].message);
    //     if(ai_response.choices[0].message.tool_calls==null){
    //         combined_word = ai_response.choices[0].message.content;
    //     }else{
    //         combined_word = ai_response.choices[0].message.tool_calls[0].function.arguments.answer;
    //     }

    cacheNewWord(firstWord, secondWord, combined_word, emoji);

    return {result: combined_word, emoji: emoji};

}

async function craft_new_card_from_cache(word) {
    let cachedResult = await db.get('SELECT name, rarity, category, health FROM card_cache WHERE name = ?', [word]);
    return cachedResult;
}

async function cacheNewCard(name, rarity, category, health) {
    await db.run('INSERT INTO card_cache (name, rarity, category, health) VALUES (?, ?, ?, ?)', [name, rarity, category, health]);
}

async function craft_new_card(word) {
    const cachedResult = await craft_new_card_from_cache(word);
    if (cachedResult) {
        return cachedResult;
    }

    const llamaAPI = new LlamaAI(apiToken);
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
    "Each card must have a rarity, category, and health." +
    "The card's rarity is based on the word's importance, size, or complexity." +
    "The card's category is the broader type of object the word represents, such as animals, math equations, famous people, etc." +
    "Health is a number from 10 to 200, based on the word's complexity, size, or importance." +
    "YOU MUST Provide the card's rarity, category, and health. Do not provide any other information or text explaning the answer.";
    
    let albumAnswerPrompt = word
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
                                description: "The category of the card based on the word: "+ albumAnswerPrompt,
                            },
                            rarity: {
                                type: "string",
                                enum: ["common", "rare", "epic", "legendary", "mythic"],
                                description: "The rarity of the card based on the word: "+ albumAnswerPrompt+ ". One word that is either common, rare, epic, legendary, or mythic.",
                            },
                            health: {
                                type: "integer",
                                description: "The health of the card",
                            },
                        },
                    },
                    required: ["rarity", "category", "health"],
                    strict: true,
                }
            }
        ],
        tool_choice: "create_card",
        max_tokens: 200
    }
    
    //setId(id + 1);
    let card_response = await inference.chatCompletion(card_api_request_json)
        .catch(error => {
            let answerIndexStart = error.message.indexOf("{");
            let answerIndexEnd = error.message.lastIndexOf("}");
            let answer = error.message.substring(answerIndexStart, answerIndexEnd+1);
            console.log(answer);
            card_response = JSON.parse(answer);
            
        });
    // await llamaAPI.run(card_api_request_json)
    //     .then(response => {
    //     // Process response
    //     card_response = response.choices[0].message;
    //     console.log(response.choices[0].message.tool_calls[0]);
    //     })
    //     .catch(error => {
    //     // Handle errors
    //     });
    // if (card_response == null) {
    //     console.log("Card response is null");
    //     return null;
    // }
    console.log(card_response.choices[0].message.tool_calls[0])

    
    let combined_card = {
        "name": albumAnswerPrompt,
        "rarity": card_response.choices[0].message.tool_calls[0].function.arguments.rarity,
        "category": card_response.choices[0].message.tool_calls[0].function.arguments.category,
        "health": card_response.choices[0].message.tool_calls[0].function.arguments.health
    }

    cacheNewCard(combined_card.name, combined_card.rarity, combined_card.power, combined_card.health);
    
    return combined_card;

    // let card = {
    //     "id": id+1,
    //     "health": combined_card.health,
    //     "power": combined_card.power,
    //     "name": combined_card.name,
    //     "emoticon": combined_card.emoji
    // };

    // let card = {
    //     "id": id,
    //     "health": 10,
    //     "power": 10,
    //     "name": combined_word,
    //     "emoticon": "🃏"
    // }

    // cards.unshift(card);
    // setCards([...cards]);
    // console.log(cards);
    
}
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

async function setupLlama() {

    const __dirname = path.dirname(fileURLToPath(import.meta.url));
    const llama =await getLlama();
    const model = await llama.loadModel({
        modelPath: path.join(__dirname, "models", "mistral-7b-instruct-v0.1.Q4_K_M.gguf"),
    });
    const context = await model.createContext();
    const session = new LlamaChatSession({
        contextSequence: context.getSequence(),
    });

    const grammar = await llama.createGrammarForJsonSchema({
        "type": "object",
        "properties": {
            "answer": {
                "type": "string"
            },
        }
    });
}

export { craft_new_word, capitalizeFirstLetter, craft_new_card };