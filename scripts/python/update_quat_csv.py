"""
  convert 'photo_record.csv' to 'photo_record_quat.csv' using colmap results
"""
import csv
import os
import sys
import numpy as np
from scipy.spatial.transform import Rotation as R


class Frame:
    def __init__(self, lat, lon, alt, qw, qx, qy, qz):
        self.lat = lat   # 纬度
        self.lon = lon   # 经度
        self.alt = alt   # 高度
        # quat为enu下的姿态
        self.qw = qw     # 四元数w分量
        self.qx = qx     # 四元数x分量
        self.qy = qy     # 四元数y分量
        self.qz = qz     # 四元数z分量

    def from_quat(self, qw, qx, qy, qz):
        self.qw = qw     # 四元数w分量
        self.qx = qx     # 四元数x分量
        self.qy = qy     # 四元数y分量
        self.qz = qz     # 四元数z分量

    def quat(self):
        return self.qx, self.qy, self.qz, self.qw

    def llh(self):
        return self.lat, self.lon, self.alt


def csv_to_frames(input_file_path):
    frames = []
    frame_names = []
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
            line = row[0] + ',' + row[1]
            parts = line.strip().split()
            file_path = parts[0]
            file_name = os.path.basename(file_path)
            roll, pitch, yaw = map(float, parts[4:7])
            Rz = R.from_euler("z", yaw, degrees=True)
            Ry = R.from_euler("y", pitch, degrees=True)
            Rx = R.from_euler("x", roll, degrees=True)
            R_ned_body = Rz * Ry * Rx
            R_body_camera = R.from_euler("z", -90.0, degrees=True)

            Rz0 = R.from_euler("z", 90.0, degrees=True)
            Ry0 = R.from_euler("y", 0.0, degrees=True)
            Rx0 = R.from_euler("x", 180.0, degrees=True)
            R_enu_ned = Rz0 * Ry0 * Rx0

            R_enu_camera = R_enu_ned * R_ned_body * R_body_camera
            qx, qy, qz, qw = R_enu_camera.as_quat()
            lat, lon, alt = map(float, parts[1:4])
            f = Frame(lat, lon, alt, qw, qx, qy, qz)
            frames.append(f)
            frame_names.append(file_name)

    return frames, frame_names


def update_by_colmap(frames, frame_names, colmap_file_path):
    with open(colmap_file_path, 'r') as input:
        lines = input.readlines()

    for i, line in enumerate(lines):
        data_list = line.strip().split()
        qw, qx, qy, qz = map(float, data_list[1:5])
        fn = data_list[9]
        ind = frame_names.index(fn)
        print("before:", R.from_quat(
            frames[ind].quat()).as_euler('zxy', degrees=True))
        frames[ind].from_quat(qw, qx, qy, qz)
        print("update:", R.from_quat(
            frames[ind].quat()).as_euler('zxy', degrees=True))

    return frames, frame_names


def write_photo_csv(frames, frame_names, output_file_path):
    cnt = len(frames)
    with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=' ')
        for i in range(cnt):
            fn = frame_names[i]
            lat, lon, alt = frames[i].llh()
            qx, qy, qz, qw = frames[i].quat()
            new_row = [fn, lat, lon, alt, qw, qx, qy, qz]
            writer.writerow(new_row)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_file_path> <colmap_file_path> <output_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    colmap_file_path = sys.argv[2]
    output_file_path = sys.argv[3]
    frames, frame_names = csv_to_frames(input_file_path)
    frames, frame_names = update_by_colmap(
        frames, frame_names, colmap_file_path)
    write_photo_csv(frames, frame_names, output_file_path)
