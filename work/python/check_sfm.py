"""
    统计images.txt与原本图像个数的比例是否超过一定比例
    Zhihao Zhan
"""
import sys
import os

def valid_percent(images_txt_path, input_folder):
    lines = []
    with open(images_txt_path, 'r') as input:
        lines = input.readlines()
    res_num = (len(lines) - 4) / 2

    file_count = 0
    for _, _, files in os.walk(input_folder):
        file_count += len(files)

    return res_num / file_count * 100.0
    


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <images_txt_path> <input_folder>")
        sys.exit(1)

    images_txt_path = sys.argv[1]
    input_folder = sys.argv[2]
    percent = valid_percent(images_txt_path, input_folder)
    if percent > 75.0:
        sys.exit(0)
    else:
        sys.exit(-1)