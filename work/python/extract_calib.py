"""
  根据图片的LLH选择用于标定的图片
  Zhihao Zhan
"""

import os
import sys
import numpy as np
from pyproj import Proj, transform


def ecef_data(input_file_path):
    data = []
    image_names = []
    ecef = Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    wgs84 = Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    # gps.txt每行格式：图片名 纬度 经度 高程，无表头
    with open(input_file_path, mode='r', encoding='utf-8') as infile:
        for line in infile:
            parts = line.strip().split()
            if not parts:
                continue
            file_name = os.path.basename(parts[0])
            lat, lon, alt = map(float, parts[1:4])
            ecef_x, ecef_y, ecef_z = transform(
                wgs84, ecef, lon, lat, alt, radians=False)
            data.append([ecef_x, ecef_y, ecef_z])
            image_names.append(file_name)

    return np.array(data), image_names


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


def get_calib_wp_file(wp_arr, image_names, num, thresold):
    wp_size = wp_arr.shape[0]
    idx = -1
    for i in range(wp_size - num + 1):
        points = wp_arr[i:i+num, :]
        lam1_div_lam0 = pca(points)
        print(lam1_div_lam0)
        if lam1_div_lam0 > thresold:
            idx = i
            break

    image_list = []
    if idx >= 0:
        for i in range(num):
            image_list.append(image_names[idx + i])

    return image_list


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python extract_calib.py <gps_file_path> <calib_wp_num> <output_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    calib_wp_num = int(sys.argv[2])
    output_file_path = sys.argv[3]
    output_folder = os.path.dirname(output_file_path)
    print(output_folder)

    wp_arr, image_names = ecef_data(input_file_path)
    image_list = get_calib_wp_file(wp_arr, image_names, calib_wp_num, 0.04)
    if (len(image_list) > 0):
        with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
            # 写入新文件
            for fn in image_list:
                outfile.write(fn + '\n')
