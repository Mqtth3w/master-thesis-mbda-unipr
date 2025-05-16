"""
@author Mqtth3w https://github.com/Mqtth3w
@license GPL-3.0
"""

import re

def evaluate(INTERFACE_DELIMITER, RESULTS_FILE):
    # load data
    with open(f"./QA/questions_{INTERFACE_DELIMITER}.txt", "r") as f:
        questions_all = [line.strip() for line in f if line.strip()]

    with open(f"./QA/answers_{INTERFACE_DELIMITER}.txt", "r") as f:
        answers_all = [line.strip() for line in f if line.strip()]

    with open(RESULTS_FILE, "r") as f:
        content = f.read()

    # extract questions
    q_block = re.search(r"QUESTIONS:\n(.*?)\n\nMODEL ANSWER:", content, re.DOTALL)
    if not q_block:
        raise ValueError("QUESTIONS' block not found")
    model_prompted_questions = [q.strip() for q in q_block.group(1).split("\n") if q.strip()]

    # extract model questions and answers
    '''
    model_qas = re.findall(
        r'(?:\d+\.\s*|Q[:\-]\s*|Question[:\-]?\s*)?(What .*?\?)\s*\n?\s*\*{0,2}Answer[:\-]?\*{0,2}\s*(.*)',
        content,
        re.IGNORECASE
    )
    '''
    model_qas = re.findall(
        r'(?:\d+\.\s*|Q[:\-]\s*|Question[:\-]?\s*)?(What is connected to .*?\?)\s*\n\s*(?:A:|Answer:|**A:**)\s*(.*?)\n', 
        content
    )
    if len(model_qas) != len(model_prompted_questions):
        raise ValueError(f"Questions mismatch ({len(model_prompted_questions)}) vs model answers ({len(model_qas)})")

    def ensure_the_in_question(q):
        return re.sub(
            r'\b(connected to\s+)(?!the\b)',
            r'\1the ',
            q,
            flags=re.IGNORECASE
        )

    model_answered_questions = [q.strip() for q, _ in model_qas]
    model_answered_questions = [ensure_the_in_question(q) for q in model_answered_questions]
    model_answers = [a.strip() for _, a in model_qas]

    # questions accuracy
    question_match_accuracy = 0
    matched_indexes = []
    for q in model_answered_questions:
        if q in questions_all:
            question_match_accuracy += 1
            matched_indexes.append(questions_all.index(q))
        else:
            matched_indexes.append(None)

    # answers accuracy
    answer_match_accuracy = 0
    for i, idx in enumerate(matched_indexes):
        if idx is None:
            continue
        expected = answers_all[idx].strip().lower().rstrip(".")
        predicted = model_answers[i].strip().lower().rstrip(".")
        if expected == predicted:
            answer_match_accuracy += 1

    # print and save 
    with open(RESULTS_FILE, "a") as f: 
        total = len(model_prompted_questions)
        cq = f"Correct questions: {question_match_accuracy}/{total} ({question_match_accuracy / total * 100:.1f}%)"
        ca = f"Correct answers {answer_match_accuracy}/{total} ({answer_match_accuracy / total * 100:.1f}%)"
        print(cq)
        print(ca)
        f.write("\n\nAUTOMATIC EVALUATION:\n" + cq + "\n" + ca)


if __name__ == "__main__":
    # choose between 
    # 'txt' textual description of the network topology
    # 'json' json //
    # 'table' tabular //
    PROMPT_TYPE = "txt"

    # chose between
    # 'colon' (: e.g., Server:eth0)
    # 'dash' (- e.g., Server-eth0) 
    INTERFACE_DELIMITER = "dash"

    # choose model between
    # 'llama' meta-llama/llama3.2-3B-Instruct (TESTED)
    # 'gemma' google/gemma-3-4b-it (EXPERIMENTAL) # needs vision support library "timm" compatible
    # 'phi' microsoft/Phi-4-mini-instruct (EXPERIMENTAL) # looks too heavy, too slow 8bit quant
    # 'phir' microsoft/Phi-4-mini-reasoning (EXPERIMENTAL) # looks too heavy, too slow 8bit quant
    # 'mistral' mistralai/Mistral-7B-Instruct-v0.3 (EXPERIMENTAL) 
    # 'qwen' ?
    MODEL = "phir"

    # set the timestamp
    RESULTS_FILE = f"./prompt_{PROMPT_TYPE}_tests/{INTERFACE_DELIMITER}/prompt_{PROMPT_TYPE}_{MODEL}_model_answer_2025-05-14T10_58_10.txt"

    evaluate(INTERFACE_DELIMITER, RESULTS_FILE)