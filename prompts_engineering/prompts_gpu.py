"""
@author Mqtth3w https://github.com/Mqtth3w
@license GPL-3.0
"""

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
from torch import float16
from torch.cuda import empty_cache, ipc_collect
from random import shuffle
from time import time
from datetime import datetime
from evaluator import evaluate

# clean GPU memory
empty_cache()
ipc_collect()

# choose between 
# 'txt' textual description of the network topology
# 'json' json //
# 'tabular' tabular //
PROMPT_TYPE = "json" 

# chose between
# 'colon' (: e.g., Server:eth0)
# 'dash' (- e.g., Server-eth0) 
INTERFACE_DELIMITER = "dash"

# choose model between
# 'llama' meta-llama/llama3.2-3B-Instruct (TESTED)
# 'gemma' google/gemma-3-4b-it (EXPERIMENTAL) # needs vision support library "timm" compatible
# 'phi' microsoft/Phi-4-mini-instruct (EXPERIMENTAL) # looks too heavy, too slow 8bit quant
# 'phir' microsoft/Phi-4-mini-reasoning (PARTIALLY TESTED) # looks 2x/3x slower than llama but it has better performances
# 'mistral' mistralai/Mistral-7B-Instruct-v0.3 (EXPERIMENTAL) # supported only with 4bit quantization, bad performances and lack of prompt understanding
# 'qwen' ?
MODEL = "phir"

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
    "gemma": {
        "model_id": "google/gemma-3-4b-it",
        "quantization_config": BitsAndBytesConfig(
            load_in_8bit=True,
            bnb_8bit_compute_dtype=float16,
            bnb_8bit_use_double_quant=True,
        ),
        "questions": 30,
    },
    "phi": {
        "model_id": "microsoft/Phi-4-mini-instruct",
        "quantization_config": BitsAndBytesConfig(
            load_in_8bit=True,
            bnb_8bit_compute_dtype=float16,
            bnb_8bit_use_double_quant=True,
            #bnb_4bit_quant_type='nf4',
        ),
        "questions": 25,
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
    },
    "mistral": {
        "model_id": "mistralai/Mistral-7B-Instruct-v0.3",
        "quantization_config": BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type='nf4',
        ),
        "questions": 25,
    },
}

def main():
    # set up the model and measure elapsed time
    timestamp = datetime.now().isoformat(timespec='seconds').replace(":", "_")
    start = time()
    model = AutoModelForCausalLM.from_pretrained(
        model_conf_data[MODEL]["model_id"],
        device_map="auto",
        torch_dtype=float16,
        quantization_config=model_conf_data[MODEL]["quantization_config"]
    )
    tokenizer = AutoTokenizer.from_pretrained(model_conf_data[MODEL]["model_id"])
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer
    )
    middle = time()

    # read the prompt data and the questions to verify the model is learning/understanding the network topology 
    # by questions and successive evaluation
    with open(f"./prompt_{PROMPT_TYPE}_tests/prompt_{PROMPT_TYPE}_{INTERFACE_DELIMITER}.txt", "r", encoding="utf-8") as f:
        prompt_definition = f.read()

    with open(f"./QA/questions_{INTERFACE_DELIMITER}.txt", "r", encoding="utf-8") as f:
        questions = f.read().splitlines()

    shuffle(questions)
    questions = "\n".join(questions[:model_conf_data[MODEL]["questions"]])

    messages = [
        {"role": "system", "content": prompt_definition},
        {"role": "user", "content": questions}
    ]

    outputs = pipe(
        messages,
        max_new_tokens=128001
    )

    end = time()
    out = outputs[0]['generated_text'][-1]['content']
    print(len(out), out, end="\n\n\n")
    elapsed_time_info = f"time (seconds): elapsed for setup {round(middle - start, 4)}, elapsed for generation {round(end - middle, 4)}, total elapsed {round(end - start, 4)}"
    print(elapsed_time_info)

    # save the output for future checks
    RESULTS_FILE = f"./prompt_{PROMPT_TYPE}_tests/{INTERFACE_DELIMITER}/prompt_{PROMPT_TYPE}_{MODEL}_model_answer_{timestamp}.txt"
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write(f"QUESTIONS:\n{questions}\n\nMODEL ANSWER:\n{out}\n\nINFO:\n{elapsed_time_info}")

    evaluate(INTERFACE_DELIMITER, RESULTS_FILE)

if __name__ == "__main__":
    main()