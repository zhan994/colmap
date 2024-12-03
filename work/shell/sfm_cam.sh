#!/bin/sh

# 固定内参共享的SFM
# Zhihao Zhan

log_time() {
    date "+%Y-%m-%d %H:%M:%S:%3N"
}

PROJECT="${PWD}/proj"

echo "$(log_time) feature extractor ..."
./build/src/colmap/exe/colmap feature_extractor \
  --ImageReader.single_camera 1 \
  --ImageReader.camera_model OPENCV \
  --ImageReader.camera_params "615.0, 615.0, 270, 270, 0.15, -0.12, 0.00, 0.00" \
  --SiftExtraction.use_gpu 1 \
  --SiftExtraction.max_image_size 1024 \
  --SiftExtraction.max_num_features 3000 \
  --database_path ${PROJECT}/database.db \
  --image_path ${PROJECT}/images
echo "$(log_time) feature_extractor done."

echo "$(log_time) feature matcher ..."
./build/src/colmap/exe/colmap  exhaustive_matcher\
  --SiftMatching.use_gpu 1 \
  --database_path ${PROJECT}/database.db
echo "$(log_time) feature exhaustive_matcher done."

mkdir -p ${PROJECT}/sparse

echo "$(log_time) colmap mapper ..."
./build/src/colmap/exe/colmap mapper \
  --Mapper.ba_refine_principal_point 0 \
  --Mapper.ba_refine_focal_length 0 \
  --Mapper.ba_refine_extra_params 0 \
  --Mapper.ba_local_max_num_iterations 50 \
  --Mapper.ba_global_max_num_iterations 100 \
  --database_path ${PROJECT}/database.db \
  --image_path ${PROJECT}/images \
  --output_path ${PROJECT}/sparse
echo "$(log_time) colmap mapper done."

# echo "$(log_time) glomap mapper ..."
# ../simple_glomap/build/simple_glomap mapper \
#   --database_path ${PROJECT}/database.db \
#   --image_path ${PROJECT}/images \
#   --output_path ${PROJECT}/sparse
# echo "$(log_time) glomap mapper done."