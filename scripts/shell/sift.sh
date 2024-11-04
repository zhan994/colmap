#!/bin/sh

# script to run feature extractor and feature matcher
# Zhihao Zhan

log_time() {
    date "+%Y-%m-%d %H:%M:%S:%3N"
}

PROJECT="${PWD}/proj"

echo "$(log_time) feature extractor..."
./build/src/colmap/exe/colmap feature_extractor \
  --ImageReader.single_camera 1 \
  --ImageReader.camera_model OPENCV \
  --ImageReader.camera_params "552.23198503638389,553.3633964901785,270,270,0.18643355235419351,-0.19986311220817557,-0.0011286505008237298,-0.00026876497068803516" \
  --SiftExtraction.use_gpu 1 \
  --SiftExtraction.max_image_size 1024 \
  --SiftExtraction.max_num_features 1000 \
  --database_path ${PROJECT}/database.db \
  --image_path ${PROJECT}/images
echo "$(log_time) feature_extractor done."

echo "$(log_time) feature matcher..."
./build/src/colmap/exe/colmap sequential_matcher \
  --SequentialMatching.overlap 10  \
  --SiftMatching.use_gpu 1 \
  --database_path ${PROJECT}/database.db
echo "$(log_time) feature exhaustive_matcher done."