import {fileURLToPath} from "url";
import path from "path";
import {getLlama, LlamaChatSession} from "node-llama-cpp";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const llama =await getLlama();
const model = await llama.loadModel({
    modelPath: path.join(__dirname, "models", "mistral-7b-instruct-v0.1.Q4_K_M.gguf"),
});
const context = await model.createContext();
const session = new LlamaChatSession({
    contextSequence: context.getSequence(),
});

let firstWord = "Dinner";
let secondWord = "Eiffel Tower";

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
"The answer has to be related to both words and the context of the words and may not contain the words themselves. " ;
//"also provide an emoji in UTF-8 encoding that represents the word.";
const emojiSystemPrompt = 'Reply with one emoji representing the word. Use the UTF-8 encoding.';
let answerPrompt = firstWord + " and " + secondWord;

const grammar = await llama.createGrammarForJsonSchema({
    "type": "object",
    "properties": {
        "answer": {
            "type": "string"
        },
    }
});

const promp = '<s>[INST] ' +
systemPrompt +
answerPrompt + '[/INST]</s>\n';

const result = await session.prompt(promp, {
    grammar,
    maxTokens: context.contextSize
});

console.log(result);