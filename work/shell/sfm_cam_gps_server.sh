#!/bin/sh

# 固定内参共享的SFM，并GPS信息对齐，colmap目录下准备好proj文件夹以及图片
# /root/colmap_detailed/work/shell/sfm_cam_gps_server.sh images_folder fx,fy,cx,cy,k1,k2,p1,p2
# Zhihao Zhan

log_time() {
    date "+%Y-%m-%d %H:%M:%S:%3N"
}

FP="$1"
CAM_PARAM="$2"
PROJECT="${FP}/proj"
mkdir -p ${PROJECT}/images
mv ${FP}/*.JPG ${PROJECT}/images
python3 /root/colmap_detailed/work/python/exif_to_gps.py ${PROJECT}/images ${PROJECT}/gps.txt

echo "$(log_time) feature extractor ..."
/root/colmap_detailed/build/src/colmap/exe/colmap feature_extractor \
  --ImageReader.single_camera 1 \
  --ImageReader.camera_model OPENCV \
  --ImageReader.camera_params ${CAM_PARAM} \
  --SiftExtraction.use_gpu 1 \
  --SiftExtraction.max_image_size 1024 \
  --SiftExtraction.max_num_features 3000 \
  --database_path ${PROJECT}/database.db \
  --image_path ${PROJECT}/images
echo "$(log_time) feature_extractor done."

echo "$(log_time) feature matcher ..."
/root/colmap_detailed/build/src/colmap/exe/colmap exhaustive_matcher \
  --SiftMatching.use_gpu 1 \
  --database_path ${PROJECT}/database.db
echo "$(log_time) feature exhaustive_matcher done."

mkdir -p ${PROJECT}/sparse
echo "$(log_time) colmap mapper ..."
/root/colmap_detailed/build/src/colmap/exe/colmap mapper \
  --Mapper.ba_refine_principal_point 0 \
  --Mapper.ba_refine_focal_length 0 \
  --Mapper.ba_refine_extra_params 0 \
  --Mapper.ba_local_max_num_iterations 25 \
  --Mapper.ba_global_max_num_iterations 50 \
  --database_path ${PROJECT}/database.db \
  --image_path ${PROJECT}/images \
  --output_path ${PROJECT}/sparse
echo "$(log_time) colmap mapper done."

echo "$(log_time) processing sparse folder..."
LARGEST_FOLDER=$(find ${PROJECT}/sparse/* -maxdepth 0 -type d -print0 | xargs -0 du -sb | sort -n -r | head -n 1 | awk '{print $2}')
if [ -z ${LARGEST_FOLDER} ]; then
    echo "$(log_time) no valid sparse folder found!"
    exit 1
fi
echo "$(log_time) largest folder is ${LARGEST_FOLDER}, export valid data as txt ..."
mv ${LARGEST_FOLDER} ${PROJECT}/sparse/valid
/root/colmap_detailed/build/src/colmap/exe/colmap model_converter \
    --input_path ${PROJECT}/sparse/valid \
    --output_path ${PROJECT}/sparse/valid \
    --output_type TXT
echo "$(log_time) export valid data as txt done."

mkdir -p ${PROJECT}/sparse/valid_aligned_enu
echo "$(log_time) ENU align ..."
/root/colmap_detailed/build/src/colmap/exe/colmap model_aligner \
    --input_path  ${PROJECT}/sparse/valid \
    --output_path  ${PROJECT}/sparse/valid_aligned_enu \
    --ref_images_path ${PROJECT}/gps.txt \
    --ref_is_gps 1 \
    --alignment_type enu \
    --alignment_max_error 3
echo "$(log_time) ENU align done."

echo "$(log_time) export ENU as txt ..."
/root/colmap_detailed/build/src/colmap/exe/colmap model_converter \
    --input_path ${PROJECT}/sparse/valid_aligned_enu \
    --output_path ${PROJECT}/sparse/valid_aligned_enu \
    --output_type TXT
echo "$(log_time) export ENU as txt done."

mkdir -p ${PROJECT}/sparse/valid_aligned_ecef
echo "$(log_time) ECEF align ..."
/root/colmap_detailed/build/src/colmap/exe/colmap model_aligner \
    --input_path  ${PROJECT}/sparse/valid \
    --output_path  ${PROJECT}/sparse/valid_aligned_ecef \
    --ref_images_path ${PROJECT}/gps.txt \
    --ref_is_gps 1 \
    --alignment_type ecef \
    --alignment_max_error 3
echo "$(log_time) ECEF align done."

echo "$(log_time) export ECEF as txt ..."
/root/colmap_detailed/build/src/colmap/exe/colmap model_converter \
    --input_path ${PROJECT}/sparse/valid_aligned_ecef \
    --output_path ${PROJECT}/sparse/valid_aligned_ecef \
    --output_type TXT
echo "$(log_time) export ECEF as txt done."

echo "$(log_time) convert camera pose from Tcw to Twc ..."
python3 /root/colmap_detailed/work/python/colmap_pose.py \
  ${PROJECT}/sparse/valid_aligned_enu/images.txt \
  ${PROJECT}/sparse/valid_aligned_enu/images_Twc.txt
python3 work/python/colmap_pose.py \
  ${PROJECT}/sparse/valid_aligned_ecef/images.txt \
  ${PROJECT}/sparse/valid_aligned_ecef/images_Twc.txt
echo "$(log_time) camera pose conversion done."

echo "$(log_time) update images_Twc.txt ..."
python3 /root/colmap_detailed/work/python/update_Twc.py \
  ${PROJECT}/gps.txt \
  ${PROJECT}/sparse/valid_aligned_ecef/images_Twc.txt \
  ${PROJECT}/sparse/valid_aligned_ecef/points3D.txt \
  ${PROJECT}/sparse/valid_aligned_ecef/images_Twc_updated.txt
echo "$(log_time) update images_Twc.txt done."

echo "$(log_time) generate photo_record_quat.csv ..."
python3 /root/colmap_detailed/work/python/colmap_quat_csv.py \
  ${PROJECT}/sparse/valid_aligned_ecef/images_Twc_updated.txt \
  ${PROJECT}/sparse/valid_aligned_enu/images_Twc.txt \
  ${PROJECT}/photo_record_quat.csv
echo "$(log_time) photo_record_quat.csv generation done."
