# retrieval_service\tools\split_jsonl_head.py

import os

input_path = os.path.normpath("retrieval_service/data/documents/medical/raw/vinmec_data_prepared.jsonl")
output_path = os.path.normpath("retrieval_service/data/documents/medical/raw/small_vinmec_data_prepared.jsonl")
num_lines = 10                    

with open(input_path, "r", encoding="utf-8") as infile, \
     open(output_path, "w", encoding="utf-8") as outfile:
    for i, line in enumerate(infile):
        if i >= num_lines:
            break
        outfile.write(line)

print(f"✅ Đã tạo file '{output_path}' với {num_lines} JSON đầu tiên từ '{input_path}'")
