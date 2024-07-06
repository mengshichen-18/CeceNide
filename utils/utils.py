import json
from collections import OrderedDict
import random


def add_id_data():
    in_path = "../data/gzy2024_sample_quiz.jsonl"
    out_path = "../data/gzy2024_sample_id_quiz.jsonl"
    with open(in_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    
    with open(out_path, 'w', encoding='utf-8') as outfile:
        for idx, line in enumerate(lines):
            data = json.loads(line, object_pairs_hook=OrderedDict)
            new_data = OrderedDict()
            new_data["id"] = idx
            new_data.update(data)
            data_str = json.dumps(new_data, ensure_ascii=False)
            outfile.write(data_str + '\n')


def remove_id_data():
    in_path = "../data/gzy2024_test_quiz.jsonl"
    out_path = "../data/gzy2024_origin_quiz.jsonl"
    with open(in_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    
    with open(out_path, 'w', encoding='utf-8') as outfile:
        for line in lines:
            data = json.loads(line)
            del data["id"]
            data_str = json.dumps(data, ensure_ascii=False)
            outfile.write(data_str + '\n')


def remove_duplicated_data():
    in_path = "../data/gzy2024_origin_quiz.jsonl"
    out_path = "../data/gzy2024_final_quiz.jsonl"
    
    seen = set()
    deduplicates = []

    with open(in_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
        for line in lines:
            if line not in seen:
                seen.add(line)
                deduplicates.append(line)

    print(f"原来共{len(lines)}条数据，现在共{len(deduplicates)}条数据\n")
    
    with open(out_path, 'w', encoding='utf-8') as outfile:
        for line in deduplicates:
            data = json.loads(line)
            data_str = json.dumps(data, ensure_ascii=False)
            outfile.write(data_str + '\n')


def sample_data(n_sample: int):
    in_path = "../data/gzy2024_final_quiz.jsonl"
    out_path = "../data/gzy2024_sample_quiz.jsonl"

    with open(in_path, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    random_lines = random.sample(lines, n_sample)
    
    with open(out_path, 'w', encoding='utf-8') as outfile:
        for line in random_lines:
            data = json.loads(line)
            data_str = json.dumps(data, ensure_ascii=False)
            outfile.write(data_str + '\n')

if __name__ == "__main__":
    add_id_data()
    # remove_duplicated_data()
    # sample_data(200)