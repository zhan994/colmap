"""
  convert 'photo_record.csv' to 'gps.txt' for model_aligner
"""
import csv
import os
import sys

def csv_to_txt(input_file_path, output_file_path):
    # 打开原始CSV文件进行读取
    with open(input_file_path, mode='r', newline='', encoding='utf-8') as infile:
        # 使用csv.reader读取CSV文件，但需要处理文件路径中的逗号
        reader = csv.reader([_f for _f in infile.read().splitlines()], delimiter=',')
        
        # 跳过前两行
        next(reader, None)
        next(reader, None)
        
        # 打开新CSV文件进行写入
        with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            # 遍历原始文件的每一行
            for row in reader:
                # 提取文件路径中的文件名
                line = row[0] + ','+ row[1]
                parts = line.strip().split()
                file_path = parts[0]
                file_name = os.path.basename(file_path)
                # 只取前四列数据，并将文件路径替换为文件名
                new_row = [file_name] + parts[1:4]
                # 写入新文件
                outfile.write(' '.join(new_row) + '\n')

    print(f"txt file: {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file_path> <output_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    csv_to_txt(input_file_path, output_file_path)