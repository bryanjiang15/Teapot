# Use a pipeline as a high-level helper
import os
from dotenv import load_dotenv
import pandas as pd
import torch
from transformers import pipeline, AutoTokenizer, DataCollatorForLanguageModeling, AutoModelForCausalLM, TrainingArguments, Trainer
from openai import OpenAI
from datasets import load_dataset
import math
import json
from huggingface_hub import InferenceClient
from diffusers import AutoPipelineForText2Image
from backend.inference_prompt import promptSpec
from backend.expansion_prompt import upgrade_promptSpec

### For testin ###
# from inference_prompt import promptSpec
# from expansion_prompt import upgrade_promptSpec

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B")

block_size = 128

load_dotenv()
hf_api_key = os.getenv("HUGGINGFACE_API_KEY")

def preprocess_function(examples):

    return tokenizer([ examples["Word1"][i]+"+"+examples["Word2"][i]+"="+examples["Result"][i] for i in range(len(examples["Result"]))])

def group_texts(examples):

    # Concatenate all texts.
    concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}

    total_length = len(concatenated_examples[list(examples.keys())[0]])

    # We drop the small remainder, we could add padding if the model supported it instead of this drop, you can

    # customize this part to your needs.

    if total_length >= block_size:

        total_length = (total_length // block_size) * block_size

    # Split by chunks of block_size.

    result = {

        k: [t[i : i + block_size] for i in range(0, total_length, block_size)]

        for k, t in concatenated_examples.items()

    }

    result["labels"] = result["input_ids"].copy()

    return result

def load_data():

    merged_words = load_dataset("csv", data_files="infinite_craft.csv", split="train")

    merged_words = merged_words.train_test_split(test_size=0.2)


    tokenized_merge = merged_words.map(

        preprocess_function,

        batched=True,

        num_proc=4,

        remove_columns=merged_words["train"].column_names,

    )

    lm_dataset = tokenized_merge.map(group_texts, batched=True, num_proc=4)

    tokenizer.pad_token = tokenizer.eos_token

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-1B", trust_remote_code=True)

    training_args = TrainingArguments(
        output_dir="merge_word_clm-model",
        eval_strategy="epoch",
        learning_rate=2e-5,
        weight_decay=0.01,
        push_to_hub=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=lm_dataset["train"],
        eval_dataset=lm_dataset["test"],
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    trainer.train()

    eval_results = trainer.evaluate()

    print(f"Perplexity: {math.exp(eval_results['eval_loss']):.2f}")

def generateWord(word1, word2, pipeline):
    prompt = word1 + "+" + word2 + "="
    # generator = pipeline("text-generation", model="merge_word_clm-model") #perplexity: 21.27
    result = pipeline(prompt, max_new_tokens=5)

    #Parse result based on trends seen in the data
    #type 1: parse the answer after "=", before "#", or "\n", 
    answer = result[0]["generated_text"].split("=")[1]
    if answer.find("#") != -1:
        answer = answer.split("#")[0]
    if answer.find("\n") != -1:
        answer = answer.split("\n")[0]
    #if a word in answer contains capital letter in the middle of the word, remove it
    for word in answer.split(" "):
        if "Question" in word and word != "Question":
            #remove Question and everything after it
            answer = answer[:answer.find("Question")]
            
    
    print("Answer: ", answer)
    return answer


def inferModel():
    client = InferenceClient(
        api_key=hf_api_key,
    )

    result = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=promptSpec["messages"],
        tools=promptSpec["tools"],
    )

    print(result["choices"][0]["message"])

def upgrade_word_inference():
    client = InferenceClient(
        api_key=hf_api_key,
    )

    result = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=upgrade_promptSpec["messages"],
        tools=upgrade_promptSpec["tools"],
    )

    print(result["choices"][0]["message"])

def generate_card():
    client = InferenceClient(
        api_key=hf_api_key,
    )
    print("Loading card spec")

    card_spec = json.load(open("card_creation.json"))

    result = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=card_spec["messages"],
        tools=card_spec["tools"],
    )

    print(result["choices"][0]["message"])

def generate_design():
    client = OpenAI()
    print("Loading design spec")

    design_spec = json.load(open("design_creation.json"))

    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=design_spec["messages"],
        tools=design_spec["tools"],
    )

    print(result.choices[0].message.tool_calls)

def generate_image():
    client = OpenAI()
    print("Loading image spec")
    prompt = "A cartoon style icon representing Mount Fuji, in modern minimalistic style, with a white background"
    image = client.images.generate(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    print(image.data[0].url)

def generate_ability():
    client = OpenAI()
    #user_prompt = open("resources/ability_craft.txt").read()
    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Can you explain the game mechanics of the multiplayer card game Magic: The Gathering? Include win condition, game objective, and game mechanics. Please respond with all direct mechanics that contribute or hinder to the win condition."}
        ]
    )
    print(result.choices[0].message.content)

if __name__ == "__main__":
    #load_data()
    # generator = pipeline("text-generation", model="merge_word_clm-model") #perplexity: 21.27
    # generateWord("Water", "Fire", generator)
    #inferModel()
    #upgrade_word_inference()
    #generate_card()
    generate_design()
    #generate_image()

# messages = [
#     {"role": "user", "content": "Who are you?"},
# ]
# pipe = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.3")
# results = pipe(messages)
# print(results) 
