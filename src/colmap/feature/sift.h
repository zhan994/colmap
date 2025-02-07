// Copyright (c) 2023, ETH Zurich and UNC Chapel Hill.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
//     * Neither the name of ETH Zurich and UNC Chapel Hill nor the names of
//       its contributors may be used to endorse or promote products derived
//       from this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.

#pragma once

#include "colmap/feature/extractor.h"
#include "colmap/feature/matcher.h"

namespace colmap {

// api: Sift特征提取参数
struct SiftExtractionOptions {
  // Number of threads for feature extraction.
  int num_threads = -1;

  // Whether to use the GPU for feature extraction.
  bool use_gpu = true;

  // Index of the GPU used for feature extraction. For multi-GPU extraction,
  // you should separate multiple GPU indices by comma, e.g., "0,1,2,3".
  std::string gpu_index = "-1";

  // Maximum image size, otherwise image will be down-scaled.
  // 最大图像尺寸，否则降采样
  int max_image_size = 3200;

  // Maximum number of features to detect, keeping larger-scale features.
  // 最大特征数，保留较大尺度的特征
  int max_num_features = 8192;

  // First octave in the pyramid, i.e. -1 upsamples the image by one level.
  // 第一组id
  int first_octave = -1;

  // Number of octaves.
  // 最小的Octave至少有16×16个像素，num_octaves = log2[min(img_h, img_w)] - 2
  int num_octaves = 4;

  // Number of levels per octave.
  // 一共 octave_res + 3 个, [-1, octave_res + 1]
  int octave_resolution = 3;

  // Peak threshold for detection.
  double peak_threshold = 0.02 / octave_resolution;

  // Edge threshold for detection.
  double edge_threshold = 10.0;

  // Estimate affine shape of SIFT features in the form of oriented ellipses as
  // opposed to original SIFT which estimates oriented disks.
  // 是否estimate_affine_shape，原始版本估计 oriented disks
  bool estimate_affine_shape = false;

  // Maximum number of orientations per keypoint if not estimate_affine_shape.
  // 不做 estimate_affine_shape 时的每个特征点的最大方向数量
  int max_num_orientations = 2;

  // Fix the orientation to 0 for upright features.
  bool upright = false;

  // Whether to adapt the feature detection depending on the image darkness.
  // Note that this feature is only available in the OpenGL SiftGPU version.
  // 仅支持OpenGL版本的SiftGPU
  bool darkness_adaptivity = false;

  // Domain-size pooling parameters. Domain-size pooling computes an average
  // SIFT descriptor across multiple scales around the detected scale. This was
  // proposed in "Domain-Size Pooling in Local Descriptors and Network
  // Architectures", J. Dong and S. Soatto, CVPR 2015. This has been shown to
  // outperform other SIFT variants and learned descriptors in "Comparative
  // Evaluation of Hand-Crafted and Learned Local Features", Schönberger,
  // Hardmeier, Sattler, Pollefeys, CVPR 2016.
  bool domain_size_pooling = false;
  double dsp_min_scale = 1.0 / 6.0;
  double dsp_max_scale = 3.0;
  int dsp_num_scales = 10;

  // Whether to force usage of the covariant VLFeat implementation.
  // Otherwise, the covariant implementation is only used when
  // estimate_affine_shape or domain_size_pooling are enabled, since the normal
  // Sift implementation is faster.
  // 是否强制使用covariant的特征提取
  // 否则默认在estimate_affine_shape和domain_size_pooling使能时采用
  // note: 普通的Sift更快
  bool force_covariant_extractor = false;

  enum class Normalization {
    // L1-normalizes each descriptor followed by element-wise square rooting.
    // This normalization is usually better than standard L2-normalization.
    // See "Three things everyone should know to improve object retrieval",
    // Relja Arandjelovic and Andrew Zisserman, CVPR 2012.
    L1_ROOT,
    // Each vector is L2-normalized.
    L2,
  };
  Normalization normalization = Normalization::L1_ROOT;

  bool Check() const;
};

// Create a Sift feature extractor based on the provided options. The same
// feature extractor instance can be used to extract features for multiple
// images in the same thread. Note that, for GPU based extraction, a OpenGL
// context must be made current in the thread of the caller. If the gpu_index is
// not -1, the CUDA version of SiftGPU is used, which produces slightly
// different results than the OpenGL implementation.
// api: 创建特征提取器
std::unique_ptr<FeatureExtractor> CreateSiftFeatureExtractor(
    const SiftExtractionOptions& options);

// api: Sift特征匹配参数
struct SiftMatchingOptions {
  // Number of threads for feature matching and geometric verification.
  int num_threads = -1;

  // Whether to use the GPU for feature matching.
  bool use_gpu = true;

  // Index of the GPU used for feature matching. For multi-GPU matching,
  // you should separate multiple GPU indices by comma, e.g., "0,1,2,3".
  std::string gpu_index = "-1";

  // Maximum distance ratio between first and second best match.
  // 最佳和次佳的比例阈值
  double max_ratio = 0.8;

  // Maximum distance to best match.
  // 最佳匹配的最大距离阈值
  double max_distance = 0.7;

  // Whether to enable cross checking in matching.
  // 是否交叉验证
  bool cross_check = true;

  // Maximum number of matches.
  // 最大匹配数
  int max_num_matches = 32768;

  // Whether to perform guided matching, if geometric verification succeeds.
  // 几何位置guide的匹配
  bool guided_matching = false;

  // Whether to use brute-force instead of FLANN based CPU matching.
  // 是否使用cpu的暴力匹配
  bool brute_force_cpu_matcher = false;

  bool Check() const;
};

std::unique_ptr<FeatureMatcher> CreateSiftFeatureMatcher(
    const SiftMatchingOptions& options);

// Load keypoints and descriptors from text file in the following format:
//
//    LINE_0:            NUM_FEATURES DIM
//    LINE_1:            X Y SCALE ORIENTATION D_1 D_2 D_3 ... D_DIM
//    LINE_I:            ...
//    LINE_NUM_FEATURES: X Y SCALE ORIENTATION D_1 D_2 D_3 ... D_DIM
//
// where the first line specifies the number of features and the descriptor
// dimensionality followed by one line per feature: X, Y, SCALE, ORIENTATION are
// of type float and D_J represent the descriptor in the range [0, 255].
//
// For example:
//
//    2 4
//    0.32 0.12 1.23 1.0 1 2 3 4
//    0.32 0.12 1.23 1.0 1 2 3 4
//
void LoadSiftFeaturesFromTextFile(const std::string& path,
                                  FeatureKeypoints* keypoints,
                                  FeatureDescriptors* descriptors);

}  // namespace colmap
