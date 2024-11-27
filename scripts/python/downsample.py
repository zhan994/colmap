'''
    Crop and Downsample Images
    Zhihao Zhan
'''
import cv2
import os
import sys

def downsample_images(input_folder_path, output_folder_path):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # 遍历文件夹中的所有文件
    for filename in os.listdir(input_folder_path):
        if filename.lower().endswith((".jpg", ".jpeg")):
            # 读取图片
            image_path = os.path.join(input_folder_path, filename)
            image = cv2.imread(image_path)
            
            # 降采样1/2
            downsampled_image = cv2.pyrDown(image)
            
            # 构建输出文件名
            
            output_path = os.path.join(output_folder_path, filename)
            
            # 保存裁剪并降采样后的图片
            cv2.imwrite(output_path, downsampled_image)
            print(f"Cropped and downsampled image saved as {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_folder_path> <output_folder_path>")
        sys.exit(1)

    input_folder_path = sys.argv[1]
    output_folder_path = sys.argv[2]

    downsample_images(input_folder_path, output_folder_path)

    print("Done cropping and downsampling images.")
