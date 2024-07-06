import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from tqdm import tqdm
import re

model_path = "/models/internlm2-20b"
data_file_path = "./data/gzy2024_1000_id_quiz.jsonl"

data = []
with open(data_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        json_obj = json.loads(line)
        data.append(json_obj)
data = data[:24]

tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, trust_remote_code=True).cuda()
model = model.eval()

def process_question_1(idx, question):
    '''
    multiple-choice question
    '''

    segments = question.split('\n')
    options = segments[-4:]
    keys = [pair.split(":")[0] for pair in options]
    values = [pair.split(":")[1] for pair in options]

    question = "\n".join(segments[:-4])
    
    output_list = []
    
    for i in range(4):
        input = "你是一个数学专家，下面是一道选择题，回答题目\n" + question + "\n" + "\n".join([f"{key}:{value}" for key, value in zip(keys, values)])
        output, history = model.chat(tokenizer, input, history=[])
        
        pattern = r"[ABCD]"
        result = re.search(pattern, output)
        if result:
            pass
        else:
            input = input + "\n" + output + "所以，选项答案是："
            output, history = model.chat(tokenizer, input, history=[])
        
        output_list.append(output)
        values.append(values.pop(0))
    
    data = {"id": idx, "type": 1, "ans": output_list,}
    
    with open('result/result.jsonl', 'a', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)
        file.write('\n')


def process_question_2(idx, question):
    '''
    fill-in-the-blank
    '''
    question = question.replace("         ", "(         )")
    input = "你是一个数学专家，正在做一道填空题。你*必须*按照格式，将所有要填入的答案在最后以列表形式输出，用[]包裹。回答问题：\n" + question
    output, history = model.chat(tokenizer, input, history=[])
        
    data = {"id": idx, "type": 2, "ans": output,}

    with open('result/result.jsonl', 'a', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)
        file.write('\n')



for question in tqdm(data):
    if question["question"].startswith("问题是"):
        process_question_1(question["id"], question["question"])
    else:
        process_question_2(question["id"], question["question"])
