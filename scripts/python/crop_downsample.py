import cv2
import os
import sys

def crop_and_downsample_images(input_folder_path, output_folder_path, crop_width, crop_height):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # 遍历文件夹中的所有文件
    for filename in os.listdir(input_folder_path):
        if filename.lower().endswith((".jpg", ".jpeg")):
            # 读取图片
            image_path = os.path.join(input_folder_path, filename)
            image = cv2.imread(image_path)
            
            # 获取图片尺寸
            height, width = image.shape[:2]
            
            # 计算裁剪的起始点（以中心为基准）
            start_x = max(width // 2 - crop_width // 2, 0)
            start_y = max(height // 2 - crop_height // 2, 0)
            
            # 裁剪图片
            cropped_image = image[start_y:start_y+crop_height, start_x:start_x+crop_width]
            
            # 降采样1/2
            downsampled_image = cv2.pyrDown(cropped_image)
            
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
    crop_width = 1080
    crop_height = 1080

    crop_and_downsample_images(input_folder_path, output_folder_path, crop_width, crop_height)

    print("Done cropping and downsampling images.")
