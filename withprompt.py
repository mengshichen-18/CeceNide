import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from tqdm import tqdm
import re

model_path = "/models/internlm2-20b"
data_file_path = "./data/dev_choice.jsonl"

data = []
with open(data_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        json_obj = json.loads(line)
        data.append(json_obj)
data = data[:24]

tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, trust_remote_code=True).cuda()
model = model.eval()

# def compute_confidence(logits, token_ids):
#     # 计算 softmax 概率
#     softmax_probs = torch.softmax(logits, dim=-1)
#     # 提取生成标记的概率
#     token_probs = softmax_probs.gather(dim=-1, index=token_ids.unsqueeze(-1)).squeeze(-1)
#     # 计算对数概率
#     log_probs = torch.log(token_probs)
#     # 归一化处理，取负数的平均值，然后求指数
#     log_confidence = -log_probs.mean().item()
# #     confidence = torch.exp(torch.tensor(normalized_log_confidence)).item()
#     normalized_confidence = 1 - 0.05*log_confidence / (0.05*log_confidence + 1)
#     return normalized_confidence
def compute_confidence(logits, token_ids, k=1):
    # 提取生成标记的 logits
    token_logits = logits.gather(dim=-1, index=token_ids.unsqueeze(-1)).squeeze(-1)
    # 计算平均 logits
    mean_logits = token_logits.mean().item()
    # 使用变种函数进行归一化和调整
    # normalized_confidence = (0.5*mean_logits) / (0.5*mean_logits + 1)
    return normalized_confidence

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
    confidence_list = []
    for i in range(4):
        input = '''角色：
            你是一个拥有卓越数学推理和解决问题能力的高度先进的人工智能系统，专门为解决数学竞赛中以LaTeX格式编写的棘手数学问题而设计。你的任务是准确分析和解决复杂的数学问题，展示对数学概念的深刻理解和强大的逻辑推理策略的应用能力。

            指令：

            仔细阅读并理解“问题”部分提供的问题陈述。
            在“问题重新陈述”部分，首先以准确无歧义的中文重新描述问题的主干题干。之后判断这是一个填空题还是选择题，他们的主要区别是在问题之后是否存在选项，选项一般由大写英文字母开头。如果有，请把选择题的选项附在提干后面。
            在“解决方案”部分，提供问题的解决方案，并详细解释你的逻辑推理过程。请记住。请记住，如果问题给出了选项则最后的答案一定在选项中出现。
            在“预答案”部分，你只需陈述最终的数字或代数答案，注意不要附加任何额外的文本或叙述。
            在“验算”部分，你需要把在“答案”中给出的答案代入原题进行验算，验算部分需要将详细检查预答案代入题干之后是否和题干条件是无冲突的。若有冲突，则重新提供问题的解决方案，并详细解释你的逻辑推理过程。请记住，如果问题给出了选项则最后的答案一定在选项中出现。然后，确定问题的答案。

            问题：
            '''
        
        
        input += question + "\n" + "\n".join([f"{key}:{value}" for key, value in zip(keys, values)])
        output, history = model.chat(tokenizer, input, history=[])
        

        
        pattern = r"[ABCD]"
        result = re.search(pattern, output)
        if result:
            pass
        else:
            input = input + "\n" + output + "所以，选项答案是："
            output, history = model.chat(tokenizer, input, history=[])
            
        
        input_ids = tokenizer.encode(input, return_tensors='pt').cuda()
        output_ids = tokenizer.encode(output, return_tensors='pt').cuda()
        full_ids = torch.cat((input_ids, output_ids), dim=1)

        with torch.no_grad():
            outputs = model(full_ids)

        # 提取生成的输出部分的 logits 和 token_ids
        logits = outputs.logits[:, -output_ids.size(1):, :]
        token_ids = output_ids
        
        print("logits:",logits)
        print("token_ids:",token_ids)

        confidence = compute_confidence(logits, token_ids)
        
        output_list.append(output)
        confidence_list.append(confidence)
        values.append(values.pop(0))
    
    data = {"id": idx, "type": 1, "ans": output_list,"confidences": confidence_list}
    
    with open('result/result_chat.jsonl', 'a', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)
        file.write('\n')


def process_question_2(idx, question):
    '''
    fill-in-the-blank
    '''
    question = question.replace("         ", "(         )")
    input =  '''角色：
            你是一个拥有卓越数学推理和解决问题能力的高度先进的人工智能系统，专门为解决数学竞赛中以LaTeX格式编写的棘手数学问题而设计。你的任务是准确分析和解决复杂的数学问题，展示对数学概念的深刻理解和强大的逻辑推理策略的应用能力。

            指令：

            仔细阅读并理解“问题”部分提供的问题陈述。
            在“问题重新陈述”部分，首先以准确无歧义的中文重新描述问题的主干题干。之后判断这是一个填空题还是选择题，他们的主要区别是在问题之后是否存在选项，选项一般由大写英文字母开头。如果有，请把选择题的选项附在提干后面。
            在“解决方案”部分，提供问题的解决方案，并详细解释你的逻辑推理过程。请记住。请记住，如果问题给出了选项则最后的答案一定在选项中出现。
            在“预答案”部分，你只需陈述最终的数字或代数答案，注意不要附加任何额外的文本或叙述。
            在“验算”部分，你需要把在“答案”中给出的答案代入原题进行验算，验算部分需要将详细检查预答案代入题干之后是否和题干条件是无冲突的。若有冲突，则重新提供问题的解决方案，并详细解释你的逻辑推理过程。请记住，如果问题给出了选项则最后的答案一定在选项中出现。然后，确定问题的答案。

            问题：
            '''  
    input += question
    input += "。你*必须*按照格式，将所有要填入的答案在最后以列表形式输出，用[]包裹。回答问题：\n"
    output, history = model.chat(tokenizer, input, history=[])
    
    input_ids = tokenizer.encode(input, return_tensors='pt').cuda()
    output_ids = tokenizer.encode(output, return_tensors='pt').cuda()
    full_ids = torch.cat((input_ids, output_ids), dim=1)

    with torch.no_grad():
        outputs = model(full_ids)
    logits = outputs.logits[:, -len(output_ids[0]):, :]
    token_ids = output_ids[:, -len(output_ids[0]):]
    confidence = compute_confidence(logits, token_ids)
        
    data = {"id": idx, "type": 2, "ans": output,"confidence": confidence}

    with open('result/result_chat.jsonl', 'a', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)
        file.write('\n')



for question in tqdm(data):
    if question["question"].startswith("问题是"):
        process_question_1(question["id"], question["question"])
    else:
        process_question_2(question["id"], question["question"])
