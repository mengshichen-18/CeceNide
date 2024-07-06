import json
import re
from tqdm import tqdm
from utils.extract_ans import extract_ans_choice, extract_ans_blank

result_file_path = "./result/result_.jsonl"
data_file_path = "./data/gzy2024_1000_id_quiz.jsonl"
score_path = "./result/score.jsonl"

def find_first_letter(s: str):
    match = re.search(r'[ABCD]', s)
    if match:
        return match.group()
    else:
        return None


def info_output(type, id, choice, multi_choice, blank):
    info = {
        'type': type,
        'id': id,
        'choice': choice,
        'multi_choice': multi_choice,  # ans_ground_truth
        'blank': blank,
    }
    with open(score_path, 'a', encoding='utf-8') as file:
        json.dump(info, file, ensure_ascii=False)
        file.write('\n')


data = []
results = []
with open(result_file_path, 'r', encoding='utf-8') as file:  # 方案的结果
    for line in file:
        json_obj = json.loads(line)
        results.append(json_obj)

with open(data_file_path, 'r', encoding='utf-8') as file:  # 对应的原始的数据集
    for line in file:
        json_obj = json.loads(line)
        data.append(json_obj)

ans1=0
ans2=0
ans3=0
total_size = len(results)
total_choice_size = 0

for result in tqdm(results):
    print("\n\n","==============\n")
    orig_data = data[result["id"]]
    answer = orig_data["answer"]

    if result["type"]==1:
        total_choice_size += 1
        answer_option = answer.keys()
        answer_option = list(answer_option)[0]
#         print("aanswer_option:",answer_option)

        index = ['D', 'C', 'B', 'A'].index(answer_option)
        answer_list = ['D', 'C', 'B', 'A'][index:] + ['D', 'C', 'B', 'A'][:index]
        
        print(answer_list)
        
        orig_ans=0
        trans_ans=0
        
        
    
        for i in range(4):
            print("result:",result["id"])
#             print("answer_list:", answer_list[i])
            if extract_ans_choice(result["ans"][i], result["id"], answer_list[i]):
                trans_ans+=1
                print("i:",i,"trans_ans:",trans_ans)
                if i==0:
                    orig_ans+=1
        print("orig_ans:",orig_ans)
        ans1 += orig_ans
        if trans_ans == 4:
            ans2 += 1
        info_output(1, result["id"], orig_ans, trans_ans, "-")

    elif result["type"]==2:
        ans_temp = extract_ans_blank(result["ans"], result["id"], answer) 
        ans3 += ans_temp
        info_output(2, result["id"], "-", "-", ans_temp)

if total_choice_size!=0:
    print(f"multi-choice orig acc: {ans1/(total_choice_size) * 100}%")
    print(f"multi-choice trans acc: {ans2/(total_choice_size)*100}%")
if (total_size-total_choice_size)!=0:
    print(f"fill-in-the-blank acc: {ans3/(total_size-total_choice_size) * 100}%")