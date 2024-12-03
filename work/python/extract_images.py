"""
    从protobuf二进制文件中提取图像数据
    Zhihao Zhan
"""
import os
import cv2
import numpy as np
import sys
from google.protobuf import message
import mapper_pb2

def save_images_from_feature_msgs(input_folder, output_folder):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 遍历输入文件夹中的所有protobuf二进制文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.bin'):
            file_path = os.path.join(input_folder, filename)
            with open(file_path, 'rb') as f:
                feature_msg = mapper_pb2.FeatureMsg()
                feature_msg.ParseFromString(f.read())

                # 从FeatureMsg中提取ImageMsg
                image_msg = feature_msg.image
                
                # 将bytes数据转换为numpy array
                image_data = np.frombuffer(image_msg.data, dtype=np.uint8)
                
                # 重新调整形状
                image_array = image_data.reshape((image_msg.height, image_msg.width, image_msg.channels))

                # 将数据转换为适合OpenCV的格式
                if image_msg.channels == 1:  # Grayscale
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2BGR)
                elif image_msg.channels == 3:  # RGB
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

                # 保存为JPEG文件
                output_filename = os.path.join(output_folder, image_msg.name)
                cv2.imwrite(output_filename, image_array)
                print(f"Saved: {output_filename}")

if __name__ == "__main__":
    # 从命令行参数获取输入和输出路径
    protobuf_dir = sys.argv[1]
    image_path = sys.argv[2]

    save_images_from_feature_msgs(protobuf_dir, image_path)
