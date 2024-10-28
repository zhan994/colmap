#!/bin/sh

PROJECT="${PWD}/proj"

log_time() {
    date "+%Y-%m-%d %H:%M:%S:%3N"
}

echo "$(log_time) convert protobuf to database..."
python3 ${PROJECT}/database.py

echo "$(log_time) feature matcher..."
./build/src/colmap/exe/colmap sequential_matcher \
  --SequentialMatching.overlap 10  \
  --SiftMatching.use_gpu 0 \
  --database_path ${PROJECT}/database.db
echo "$(log_time) feature exhaustive_matcher done."

echo "$(log_time) glomap mapper..."
./build/glomap/glomap mapper \
  --database_path ${PROJECT}/database.db \
  --image_path ${PROJECT}/images \
  --output_path ${PROJECT}/sparse
echo "$(log_time) glomap mapper done."

echo "$(log_time) convert csv to gps..."
python3 csv_to_gps.py ${PROJECT}/photo_record.csv ${PROJECT}/gps.txt
echo "$(log_time) csv conversion done."

mkdir -p ${PROJECT}/sparse/0_aligned_enu
echo "$(log_time) ENU align..."
./build/src/colmap/exe/colmap model_aligner \
    --input_path  ${PROJECT}/sparse/0 \
    --output_path  ${PROJECT}/sparse/0_aligned_enu \
    --ref_images_path ${PROJECT}/gps.txt \
    --ref_is_gps 1 \
    --alignment_type enu \
    --alignment_max_error 3
echo "$(log_time) ENU align done."

echo "$(log_time) export ENU as txt..."
./build/src/colmap/exe/colmap model_converter \
    --input_path ${PROJECT}/sparse/0_aligned_enu \
    --output_path ${PROJECT}/sparse/0_aligned_enu \
    --output_type TXT
echo "$(log_time) export ENU as txt done."

mkdir -p ${PROJECT}/sparse/0_aligned_ecef
echo "$(log_time) ECEF align..."
./build/src/colmap/exe/colmap model_aligner \
    --input_path  ${PROJECT}/sparse/0 \
    --output_path  ${PROJECT}/sparse/0_aligned_ecef \
    --ref_images_path ${PROJECT}/gps.txt \
    --ref_is_gps 1 \
    --alignment_type ecef \
    --alignment_max_error 3
echo "$(log_time) ECEF align done."

echo "$(log_time) export ECEF as txt..."
./build/src/colmap/exe/colmap model_converter \
    --input_path ${PROJECT}/sparse/0_aligned_ecef \
    --output_path ${PROJECT}/sparse/0_aligned_ecef \
    --output_type TXT
echo "$(log_time) export ECEF as txt done."

echo "$(log_time) convert camera pose from Tcw to Twc..."
python3 convert_pose.py ${PROJECT}/sparse/0_aligned_enu/cameras.txt ${PROJECT}/sparse/0_aligned_enu/cameras_twc.txt
python3 convert_pose.py ${PROJECT}/sparse/0_aligned_ecef/cameras.txt ${PROJECT}/sparse/0_aligned_ecef/cameras_twc.txt
echo "$(log_time) camera pose conversion done."

echo "$(log_time) generate photo_record_quat1.csv..."
python3 scripts/python/colmap_quat_csv.py \
  ${PROJECT}/sparse/0_aligned_ecef/images_Twc.txt \
  ${PROJECT}/sparse/0_aligned_enu/images_Twc.txt \
  ${PROJECT}/photo_record_quat1.csv
echo "$(log_time) photo_record_quat1.csv generation done."
