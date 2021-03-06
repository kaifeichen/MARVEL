#pragma once

#include "lib/adapter/rtabmap/RTABMapAdapter.h"
#include "lib/data/CameraModel.h"
#include <boost/program_options.hpp>
#include <opencv2/core/core.hpp>

namespace po = boost::program_options;

class Visualizer final {
public:
  int run(int argc, char *argv[]);

private:
  static void printInvalid(const std::vector<std::string> &opts);
  static void printUsage(const po::options_description &desc);
  Transform localize(const cv::Mat &image, const CameraModel &camera,
                     int featureLimit, int corrLimit, double distRatio);
  bool downsample(cv::Mat &image, double &scale);

private:
  RTABMapAdapter _adapter;
};
