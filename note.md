# feature_extractor

## 1 流程

- `exe/colmap.cc` 上层接口`main`；
- `exe/feature.cc` 调用`colmap::RunFeatureExtractor`；
- `controllers/feature_extraction.cc` 创建`FeatureExtractorController`控制图片读取`ImageReader`、图片下采样`ImageResizerThread`、特征提取`SiftFeatureExtractorThread`和结果写入数据库`FeatureWriterThread`；
- `feature/sift.cc` 根据参数创建对应的`FeatureExtractor`进行特征提取；
- `controllers/image_reader.cc` 对`ImageReader`图片读取的实现。

## 2 分析



# sequential_matcher

## 1 流程

- `exe/colmap.cc` 上层接口`main`；
- `exe/feature.cc`  调用`colmap::RunSequentialMatcher`；
- `controllers/feature_matching.cc`  创建带有`SequentialPairGenerator`的`GenericFeatureMatcher`来控制匹配对生成输入`FeatureMatcherController`进行特征匹配；
- `controllers/feature_matching_utils` 实现`FeatureMatcherController`控制特征匹配的过程，包含匹配`FeatureMatcherWorker`和对极几何验证`VerifierWorker`，其中`FeatureMatcherController`将外部通过`Match`接口传入的图像对插入`FeatureMatcherWorker`负责的队列，`FeatureMatcherWorker`通过实例化`FeatureMatcher`进行特征提取；
- `feature/pairing.cc` 对`SequentialPairGenerator`匹配对生成的实现；
- `feature/sift.cc`  根据参数创建对应的`FeatureMatcher`进行特征提取；
- `estimators/two_view_geometry.cc` 估计匹配后的帧间对极几何关系。

## 2 分析



# mapper

## 1 流程

- `exe/colmap.cc` 上层接口`main`；
- `exe/sfm.cc` 调用`colmap::Mapper`；
- `controllers/incremental_mapper.cc`

## 2 分析

