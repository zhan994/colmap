"""
    'photo_record_quat.csv' 结合aligned_ecef的位置和aligned_enu的姿态
    Zhihao Zhan
"""
import csv
import os
import sys

import numpy as np
from scipy.spatial.transform import Rotation as R
import pyproj
from pyproj import Proj, transform


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

def colmap_ecef(ecef_file_path):
    frames = []
    frame_names = []
    points = []
    lines = []
    with open(ecef_file_path, 'r') as input:
        lines = input.readlines()

    ecef = Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    wgs84 = Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    for i, line in enumerate(lines):
        data_list = line.strip().split()
        if data_list[0] == "POINT":
            px, py, pz = map(float, data_list[1:4])
            lon, lat, alt = transform(ecef, wgs84, px, py, pz, radians=False)
            points.append((lat, lon, alt))
        else:
            qw, qx, qy, qz, tx, ty, tz = map(float, data_list[1:8])
            fn = data_list[9]
            lon, lat, alt = transform(ecef, wgs84, tx, ty, tz, radians=False)
            f = Frame(lat, lon, alt, qw, qx, qy, qz)
            frames.append(f)
            frame_names.append(fn)
    return frames, frame_names, points


def colmap_enu(frames, frame_names, enu_file_path):
    lines = []
    with open(enu_file_path, 'r') as input:
        lines = input.readlines()

    for i, line in enumerate(lines):
        data_list = line.strip().split()
        qw, qx, qy, qz = map(float, data_list[1:5])
        fn = data_list[9]
        ind = frame_names.index(fn)
        # print("before:", R.from_quat(
        #     frames[ind].quat()).as_euler('zxy', degrees=True))
        frames[ind].from_quat(qw, qx, qy, qz)
        # print("update:", R.from_quat(
        #     frames[ind].quat()).as_euler('zxy', degrees=True))

    return frames, frame_names


def write_photo_csv(frames, cam_params, frame_names, points, output_file_path):
    with open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=' ')
        
        fx, fy, cx, cy, k1, k2, p1, p2 = map(float, cam_params)
        new_row = ["PARAM", fx, fy, cx, cy, k1, k2, p1, p2]
        writer.writerow(new_row)

        for i in range(len(frames)):
            fn = frame_names[i]
            lat, lon, alt = frames[i].llh()
            qx, qy, qz, qw = frames[i].quat()
            new_row = [fn, lat, lon, alt, qw, qx, qy, qz]
            writer.writerow(new_row)

        for i in range(len(points)):
            lat, lon, alt = points[i]
            new_row = ["POINT", lat, lon, alt]
            writer.writerow(new_row)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <cam_params> <colmap_ecef_file_path> <colmap_enu_file_path>  <output_file_path>")
        sys.exit(1)

    cam_params_str = sys.argv[1]
    colmap_ecef_file_path = sys.argv[2]
    colmap_enu_file_path = sys.argv[3]
    output_file_path = sys.argv[4]

    cam_params = cam_params_str.strip().split(',')
    frames = []
    frame_names = []
    points = []
    frames, frame_names, points = colmap_ecef(colmap_ecef_file_path)
    frames, frame_names = colmap_enu(frames, frame_names, colmap_enu_file_path)
    write_photo_csv(frames, cam_params, frame_names, points, output_file_path)
