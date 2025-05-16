from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
from torch import float16
from torch.cuda import empty_cache, ipc_collect
from random import shuffle
from time import time
from datetime import datetime
from evaluator import evaluate

def main():
    # clean GPU memory
    empty_cache()
    ipc_collect()

    model_id = "meta-llama/Llama-3.2-3B-Instruct"

    # set up the model and measure elapsed time
    timestamp = datetime.now().isoformat(timespec='seconds').replace(":", "_")
    start = time()
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        torch_dtype=float16,
        quantization_config=BitsAndBytesConfig(
            load_in_8bit=True,
            bnb_8bit_compute_dtype=float16,
            bnb_8bit_use_double_quant=True,
        ),
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer
    )
    middle = time()

    # read the prompt data and the questions to verify the model is learning/understanding the network topology 
    # by questions and successive evaluation
    with open(f"./prompt_txt_dash.txt", "r", encoding="utf-8") as f:
        prompt_definition = f.read()

    with open(f"./questions_dash.txt", "r", encoding="utf-8") as f:
        questions = f.read().splitlines()

    shuffle(questions)
    questions = "\n".join(questions)

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
    RESULTS_FILE = f"./prompt_txt_dash_model_answer_{timestamp}.txt"
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write(f"QUESTIONS:\n{questions}\n\nMODEL ANSWER:\n{out}\n\nINFO:\n{elapsed_time_info}")

    evaluate("dash", RESULTS_FILE)

if __name__ == "__main__":
    main()