#!/bin/sh

# 特征提取，colmap目录下准备好proj文件夹以及图片
# ./work/shell/sift.sh fx,fy,cx,cy,k1,k2,p1,p2
# Zhihao Zhan

log_time() {
    date "+%Y-%m-%d %H:%M:%S:%3N"
}

PROJECT=${PWD}/proj
CAM_PARAM=$1

echo "$(log_time) feature extractor ..."
./build/src/colmap/exe/colmap feature_extractor \
  --ImageReader.single_camera 1 \
  --ImageReader.camera_model OPENCV \
  --SiftExtraction.use_gpu 1 \
  --SiftExtraction.max_image_size 1024 \
  --SiftExtraction.max_num_features 1000 \
  --database_path ${PROJECT}/database.db \
  --image_path ${PROJECT}/images
echo "$(log_time) feature_extractor done."

echo "$(log_time) feature matcher ..."
./build/src/colmap/exe/colmap sequential_matcher \
  --SiftMatching.use_gpu 1 \
  --database_path ${PROJECT}/database.db
echo "$(log_time) feature exhaustive_matcher done."