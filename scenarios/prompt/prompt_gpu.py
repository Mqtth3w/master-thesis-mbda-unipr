"""
@author Mqtth3w https://github.com/Mqtth3w
@license GPL-3.0
"""

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
from torch import float16
from torch.cuda import empty_cache, ipc_collect
from time import time
import re

empty_cache()
ipc_collect()

# 1, 2 or 3 (the three scenarios)
SYSTEM_PROMPT = 1
assert SYSTEM_PROMPT in [1, 2, 3]

MODEL = "llama"
assert MODEL == "llama" or MODEL == "phir"

model_conf_data = {
    "llama": {
        "model_id": "meta-llama/Llama-3.2-3B-Instruct",
        "quantization_config": BitsAndBytesConfig(
            load_in_8bit=True,
            bnb_8bit_compute_dtype=float16,
            bnb_8bit_use_double_quant=True,
        ),
        "questions": 30,
    },
    "phir": {
        "model_id": "microsoft/Phi-4-mini-reasoning",
        "quantization_config": BitsAndBytesConfig(
            load_in_8bit=True,
            bnb_8bit_compute_dtype=float16,
            bnb_8bit_use_double_quant=True,
            #bnb_4bit_quant_type='nf4',
        ),
        "questions": 20,
    }
}

def format_messages(messages, model_name):
    if model_name == "llama":
        prompt = "" #<|begin_of_text|>
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"<|start_header_id|>system<|end_header_id|>\n{content}<|eot_id|>"
            elif role == "user":
                prompt += f"<|start_header_id|>user<|end_header_id|>\n{content}<|eot_id|>"
            elif role == "assistant":
                prompt += f"<|start_header_id|>assistant<|end_header_id|>\n{content}<|eot_id|>"
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n"
        return prompt
    elif model_name == "phir":
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"<|system|>\n{content}<|end|>\n"
            elif role == "user":
                prompt += f"<|user|>\n{content}<|end|>\n"
            elif role == "assistant":
                prompt += f"<|assistant|>\n{content}<|end|>\n"
        prompt += "<|assistant|>\n"
        return prompt
    else:
        raise ValueError("Unknown model name")

def main():
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_conf_data[MODEL]["model_id"],
            device_map="auto",
            torch_dtype=float16,
            quantization_config=model_conf_data[MODEL]["quantization_config"]
        )
        tokenizer = AutoTokenizer.from_pretrained(model_conf_data[MODEL]["model_id"])
        with open(f"../{SYSTEM_PROMPT}/system_prompt_{SYSTEM_PROMPT}.txt" , "r", encoding="utf-8") as f:
            system_prompt = f.read()
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        while user_input := input(f"\nAssistant({MODEL}): How can I help you with this system?\nYou: "):
            messages.append({"role": "user", "content": user_input})
            prompt = format_messages(messages, MODEL)
            input_ids = tokenizer(prompt, return_tensors="pt").to(model.device)
            output_ids = model.generate(
                **input_ids,
                max_new_tokens=128001,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id
            )
            full_output = tokenizer.decode(output_ids[0], skip_special_tokens=False)
            #print("\n\nFULL OUTPUT:  ", full_output, "\n\n")
            if MODEL == "llama":
                split_output = full_output.split("<|eot_id|>")
                if len(split_output) >= 2:
                    reply = split_output[-2].split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
                else:
                    reply = split_output[-1].strip() if split_output else ""
            elif MODEL == "phir":
                reply = full_output.split("<|assistant|>")[-1].strip()
                reply = reply.replace("<|end|>", "").strip()
                reply = reply.split("<|user|>")[0].strip()
                reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL)
                #reply = re.sub(r"\\boxed\{(.*?)\}", r"\1", reply)
                re.sub(r'(\\[a-zA-Z]+\{[^{}]*\}\s*)+$', '', reply).strip()
                reply = reply.strip()
            print(f"\nAssistant({MODEL}): {reply}")
            messages.append({"role": "assistant", "content": reply})

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt, Exiting.")

if __name__ == "__main__":
    main()