"""
  获取用于标定的航点数据
  Zhihao Zhan
"""

import os
import sys
import csv
import numpy as np
import pyproj
from pyproj import Proj, transform


def ecef_data(input_file_path):
    data = []
    ecef = Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    wgs84 = Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    # 打开原始CSV文件进行读取
    with open(input_file_path, mode='r', newline='', encoding='utf-8') as infile:
        # 使用csv.reader读取CSV文件，但需要处理文件路径中的逗号
        reader = csv.reader(
            [_f for _f in infile.read().splitlines()], delimiter=',')

        # 跳过前两行
        next(reader, None)
        next(reader, None)
        # 遍历原始文件的每一行
        for row in reader:
            # 提取文件路径中的文件名
            line = row[0]
            parts = line.strip().split()
            file_path = parts[0]
            file_name = os.path.basename(file_path)
            # 只取前四列数据，并将文件路径替换为文件名
            lat, lon, alt = map(float, parts[1:4])
            ecef_x, ecef_y, ecef_z = transform(
                wgs84, ecef, lon, lat, alt, radians=False)
            data.append([ecef_x, ecef_y, ecef_z])

    return np.array(data)


def pca(points):
    # 1. 中心化数据
    mean = np.mean(points, axis=0)
    centered_data = points - mean

    # 2. 计算协方差矩阵
    cov_matrix = np.cov(centered_data, rowvar=False)
    # print(cov_matrix.shape)

    # 3. 特征值分解
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)

    # 4. 特征值和特征向量排序
    sorted_indices = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[sorted_indices]
    eigenvectors = eigenvectors[:, sorted_indices]

    return eigenvalues[1] / eigenvalues[0]


def get_calib_wp_file(wp_arr, num, thresold):
    wp_size = wp_arr.shape[0]
    idx = -1
    for i in range(wp_size - num + 1):
        points = wp_arr[i:i+num, :]
        lam1_div_lam0 = pca(points)
        print(lam1_div_lam0)
        if lam1_div_lam0 > thresold:
            idx = i
            break

    pb_list = []
    if idx >= 0:
        for i in range(num):
            pb_fn = str(idx + i) + ".bin"
            pb_list.append(pb_fn)

    return pb_list


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_file_path> <calib_wp_num> <output_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    calib_wp_num = int(sys.argv[2])
    output_file_path = sys.argv[3]
    output_folder = os.path.dirname(output_file_path)
    print(output_folder)

    wp_arr = ecef_data(input_file_path)
    pb_list = get_calib_wp_file(wp_arr, calib_wp_num, 0.04)
    if (len(pb_list) > 0):
        with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
            # 写入新文件
            for fn in pb_list:
                new_row = os.path.join(output_folder, fn)
                outfile.write(new_row + '\n')
