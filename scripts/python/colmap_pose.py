"""
    convert colmap camera pose from Tcw to Twc
    Zhihao Zhan
"""
import numpy as np
from scipy.spatial.transform import Rotation as R 
import sys

def pose_from_colmap(input_file_path, output_file_path):
    lines = []
    with open(input_file_path, 'r') as input:
        lines = input.readlines()

    lines = lines[4::2]
    for i, line in enumerate(lines):
        data_list = line.strip().split()
        qw, qx, qy, qz, tx, ty, tz = map(float, data_list[1:8])
        R_cw = R.from_quat([qx, qy, qz, qw]).as_matrix()
        t_cw = np.array([tx, ty, tz])
        R_wc = R_cw.T
        t_wc = -R_wc @ t_cw
        qx_new, qy_new, qz_new, qw_new = R.from_matrix(R_wc).as_quat()
        tx_new, ty_new, tz_new = t_wc
        data_list[1:8] = [qw_new, qx_new, qy_new, qz_new, tx_new, ty_new, tz_new]
        lines[i] = ' '.join(map(str, data_list)) + '\n'
    
    with open(output_file_path, 'w') as output:
        output.writelines(lines)

    print(f"Twc from colmap: {output_file_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file_path> <output_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    pose_from_colmap(input_file_path, output_file_path)

    
