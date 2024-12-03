"""
    可视化 `images_Twc_updated.txt` 文件中的稀疏点云和相机位置
    Zhihao Zhan
"""

import sys
import os
import numpy as np
import open3d as o3d


def parse_images_twc_file(file_path):
    """
    解析 images_Twc_updated.txt 文件，提取图像的 ID、旋转、平移、相机 ID 和文件名，以及点云数据。

    :param file_path: images_Twc_updated.txt 文件的路径
    :return: 包含所有图像信息的列表和点云数据
    """
    images = []
    camera_positions = []
    point_cloud = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

        for line in lines:
            if not line.strip():
                continue  # 跳过空行

            if line.startswith("POINT"):
                # 解析点云数据
                parts = line.split()
                if len(parts) != 4 or parts[0] != "POINT":
                    continue  # 跳过不符合格式的行

                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                point_cloud.append([x, y, z])
            else:
                # 解析图像信息
                parts = line.split()
                if len(parts) < 10:
                    continue  # 跳过不符合格式的行

                image_id = int(parts[0])
                qw = float(parts[1])
                qx = float(parts[2])
                qy = float(parts[3])
                qz = float(parts[4])
                tx = float(parts[5])
                ty = float(parts[6])
                tz = float(parts[7])
                camera_id = int(parts[8])
                name = parts[9]

                images.append({
                    'image_id': image_id,
                    'qw': qw,
                    'qx': qx,
                    'qy': qy,
                    'qz': qz,
                    'tx': tx,
                    'ty': ty,
                    'tz': tz,
                    'camera_id': camera_id,
                    'name': name
                })
                camera_positions.append([tx, ty, tz])

    return images, np.array(point_cloud), np.array(camera_positions)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python visualize_txt.py <folder to search images_Twc_updated.txt> ")
        sys.exit(1)

    folder_path = sys.argv[1]
    txt_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if "images_Twc_updated.txt" in file:
                txt_files.append(os.path.join(root, file))

    images_data = []
    point_cloud_data = []
    camera_positions = []
    for file_path in txt_files:
        print(f"Processing {file_path}")
        images_data_new, point_cloud_data_new, camera_positions_new = parse_images_twc_file(
            file_path)
        images_data.extend(images_data_new)
        point_cloud_data.extend(point_cloud_data_new)
        camera_positions.extend(camera_positions_new)

    # 可视化点云数据
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(point_cloud_data)
    camera_positions_o3d = o3d.geometry.PointCloud()
    camera_positions_o3d.points = o3d.utility.Vector3dVector(camera_positions)
    o3d.visualization.draw_geometries([point_cloud, camera_positions_o3d])
