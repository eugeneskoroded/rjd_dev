import os
MODEL_NAME = os.environ['MODEL_NAME'] #"IlyaGusev/saiga2_13b_lora"
BASE_MODEL_PATH = os.environ['BASE_MODEL_PATH'] #"TheBloke/Llama-2-13B-fp16"
os.environ['TRANSFORMERS_CACHE'] = 'volume/cache'

from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import os
import flask
from flask import Flask, request, jsonify

import torch
print(f"Доступна ли CUDA: {torch.cuda.is_available()}")

app = Flask(__name__)

DEFAULT_MESSAGE_TEMPLATE = "<s>{role}\n{content}</s>\n"
DEFAULT_SYSTEM_PROMPT = "Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им."

class Conversation:
    def __init__(
        self,
        message_template=DEFAULT_MESSAGE_TEMPLATE,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        start_token_id=1,
        bot_token_id=9225
    ):
        self.message_template = message_template
        self.start_token_id = start_token_id
        self.bot_token_id = bot_token_id
        self.messages = [{
            "role": "system",
            "content": system_prompt
        }]

    def get_start_token_id(self):
        return self.start_token_id

    def get_bot_token_id(self):
        return self.bot_token_id

    def add_user_message(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })

    def add_bot_message(self, message):
        self.messages.append({
            "role": "bot",
            "content": message
        })

    def get_prompt(self, tokenizer):
        final_text = ""
        for message in self.messages:
            message_text = self.message_template.format(**message)
            final_text += message_text
        final_text += tokenizer.decode([self.start_token_id, self.bot_token_id])
        return final_text.strip()


def generate(model, tokenizer, prompt, generation_config):
    data = tokenizer(prompt, return_tensors="pt")
    data = {k: v.to(model.device) for k, v in data.items()}
    output_ids = model.generate(
        **data,
        generation_config=generation_config
    )[0]
    output_ids = output_ids[len(data["input_ids"][0]):]
    output = tokenizer.decode(output_ids, skip_special_tokens=True)
    return output.strip()

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)

config = PeftConfig.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH,
    load_in_8bit=True,
    torch_dtype=torch.float16,
    device_map="auto"
)
model = PeftModel.from_pretrained(
    model,
    MODEL_NAME,
    torch_dtype=torch.float16
)
model.eval()

generation_config = GenerationConfig.from_pretrained(MODEL_NAME)
print(generation_config)


@app.route('/ai_answer', methods=['GET'])
def receive_message():
    data = request.get_json()
    print(data)
    # Check if the 'message' key exists in the JSON data
    try:
        message = data['prompt']
        
        # input_ = f"Данные: '''{message}''' Исходя из данных {question}" 
        conversation = Conversation()
        conversation.add_user_message(message)
        prompt = conversation.get_prompt(tokenizer)
        
        output = generate(model, tokenizer, prompt, generation_config)

        # You can also send a response back to the client
        return jsonify({'answer': output})
    except Exception as e:
        return jsonify({'answer': None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
