'''
  可视化 `gps.txt` 的 UTM 轨迹
  Zhihao Zhan
'''

import sys
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Transformer

def vis_traj(gps_txt_file):
    tf = Transformer.from_crs("epsg:4326", "epsg:32649") 
    data_x = []
    data_y = []
    with open(gps_txt_file, mode='r', newline='', encoding='utf-8') as infile:
        for line in infile:
            # 去除每行的首尾空白符
            line = line.strip()
            # 分割文件名和后面的数据
            filename, *coordinates = line.split()
            # 将经纬度和高度转换为浮点数
            latitude, longitude, altitude = map(float, coordinates)
            px, py = tf.transform(latitude, longitude)
            # 将数据存储为元组
            data_x.append(px)
            data_y.append(py)
    plt.scatter(data_x, data_y)
    plt.show()


if __name__ == "__main__":
  if len(sys.argv) != 2:
        print("Usage: python script.py <gps.txt path>")
        sys.exit(1)

  input_file_path = sys.argv[1]
  vis_traj(input_file_path)
