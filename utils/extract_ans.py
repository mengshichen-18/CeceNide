# Edited from @https://github.com/open-compass/opencompass/blob/main/opencompass/utils/text_postprocessors.py

import re
import json

def find_first_letter(s: str):
    match = re.search(r'[ABCD]', s)
    if match:
        return match.group()
    else:
        return None

def info_output(type, id, ans, ans_gt):
    info_path = "./result/info.jsonl"
    info = {
        'type': type,
        'id': id,
        'ans': ans,
        'ans_gt': ans_gt,  # ans_ground_truth
    }
    with open(info_path, 'a', encoding='utf-8') as file:
        json.dump(info, file, ensure_ascii=False)
        file.write('\n')

def extract_ans_choice(text: str, id, options: str):
    match_flag = False
    patterns = [
        f'答案是?\s*([{options}])',
        f'答案是?\s*：\s*([{options}])',
        f'答案是?\s*:\s*([{options}])',
        f'答案应该?是\s*([{options}])',
        f'答案应该?选\s*([{options}])',
        f'答案是选项\s*([{options}])'
        f'答案为\s*([{options}])',
        f'答案选\s*([{options}])',
        f'选择?\s*([{options}])',
        f'故选?\s*([{options}])'
        f'只有选?项?\s?([{options}])\s?是?对',
        f'只有选?项?\s?([{options}])\s?是?错',
        f'只有选?项?\s?([{options}])\s?不?正确',
        f'只有选?项?\s?([{options}])\s?错误',
        f'说法不?对选?项?的?是\s?([{options}])',
        f'说法不?正确选?项?的?是\s?([{options}])',
        f'说法错误选?项?的?是\s?([{options}])',
        f'([{options}])\s?是正确的',
        f'([{options}])\s?是正确答案',
        f'选项\s?([{options}])\s?正确',
        f'所以答\s?([{options}])',
        f'所以\s?([{options}][.。$]?$)',
        f'所有\s?([{options}][.。$]?$)',
        f'[\s，：:,]([{options}])[。，,\.]?$',
        f'[\s，,：:][故即]([{options}])[。\.]?$',
        f'[\s，,：:]因此([{options}])[。\.]?$',
        f'[是为。]\s?([{options}])[。\.]?$',
        f'因此\s?([{options}])[。\.]?$',
        f'显然\s?([{options}])[。\.]?$',
        f'答案是\s?(\S+)(?:。|$)',
        f'答案应该是\s?(\S+)(?:。|$)',
        f'答案为\s?(\S+)(?:。|$)',
        f'[Tt]he answer is:?\s+\(?([{options}])\)?',
        f'[Tt]he answer is option:?\s+\(?([{options}])\)?',
        f'[Tt]he correct answer is:?\s+\(?([{options}])\)?',
        f'[Tt]he correct answer is option:?\s+\(?([{options}])\)?',
        f'[Tt]he answer to the question is:?\s+\(?([{options}])\)?',
        f'^选项\s?([{options}])',
        f'^([{options}])\s?选?项',
        f'(\s|^)[{options}][\s。，,：:\.$]',
        f'1.\s?(.*?)$',
        f'1.\s?([{options}])[.。$]?$',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            match_flag = True
            outputs = match.group(0)
            if options in outputs:
                return True
            else:
                info_output("wrong answer", id, outputs, options)  # check manully later
                return False

    if find_first_letter(text)==options:
        info_output("tbd", id, text, options) # check manully later
        return True
    else:
        info_output("wrong answer", id, text, options) # check manully later
        return False

def extract_ans_blank(text: str, id, answer: list):
    patterns = [
        r"\[([^\]]*)\]",
        f'答案是?\s*(.*)',
        f'答案是?\s*：\s*(.*)',
        f'答案是?\s*:\s*(.*)',
        f'答案应该?是\s*(.*)',
        f'答案应该?填\s*(.*)',
        f'答案为\s*(.*)',
        f'答案填\s*(.*)',
        f'填入?\s*(.*)',
        f'故填?\s*(.*)'
        f'(.*)\s?是正确的',
        f'(.*)\s?是正确答案',
        f'所以答\s?(.*)',
        f'所以\s?((.*)[.。\$]?$)',
        f'所有\s?((.*)[.。$]?$)',
        f'[\s，,：:][故即](.*)[。\.]?$',
        f'[\s，,：:]因此(.*)[。\.]?$',
        f'[是为。]\s?(.*)[。\.]?$',
        f'因此\s?(.*)[。\.]?$',
        f'显然\s?(.*)[。\.]?$',
        f'答案是\s?(\S+)(?:。|$)',
        f'答案应该是\s?(\S+)(?:。|$)',
        f'答案为\s?(\S+)(?:。|$)',
        f'[Tt]he answer is:?\s+\(?(.*)\)?',
        f'[Tt]he answer is option:?\s+\(?(.*)\)?',
        f'[Tt]he correct answer is:?\s+\(?(.*)\)?',
        f'[Tt]he correct answer is option:?\s+\(?(.*)\)?',
        f'[Tt]he answer to the question is:?\s+\(?(.*)\)?',
        f'^选项\s?(.*)',
        f'^(.*)\s?选?项',
        f'1.\s?(.*?)$',
        f'1.\s?(.*)[.。$]?$',        
    ]
    outputs = ""
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            match_flag = True
            outputs = match.group(0)
    if not match:
        info_output("match fail", id, text, answer)  # check manully later
    
    correct_num=0
    for ans in answer:
        ans = ans.replace("$", "")
        ans = ans.replace("－","-")
        if ans in outputs:
            correct_num+=1
        else:
            info_output("wrong answer", id, text, answer)  # check manully later
    
    return correct_num / len(answer)