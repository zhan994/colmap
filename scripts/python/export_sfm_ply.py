"""
    Export SfM data to PLY format
    Zhihao Zhan
"""

import sys
import numpy as np
import open3d as o3d


def read_point_cloud(file_path):
    """Read point cloud data from a file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    points = []
    colors = []
    for line in lines[3:]:
        if line.strip() == '':
            continue
        data = line.split()
        point = np.array([float(data[1]), float(data[2]), float(data[3])])
        color = np.array(
            [float(data[4])/255., float(data[5])/255., float(data[6])/255.])
        points.append(point)
        colors.append(color)
    return points, colors


def save_point_cloud_as_pcd(points, colors, output_file):
    """Save point cloud data to a PCD file."""
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    o3d.io.write_point_cloud(output_file, pcd)


def main():
    if len(sys.argv) != 3:
        print("Usage: python export_sfm_ply.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Read point cloud data
    points, colors = read_point_cloud(input_file)

    # Save point cloud data to PCD file
    save_point_cloud_as_pcd(points, colors, output_file)

    print(f"Point cloud saved to {output_file}")


if __name__ == "__main__":
    main()
