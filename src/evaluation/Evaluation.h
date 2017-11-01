#pragma once

#include <boost/program_options.hpp>

namespace po = boost::program_options;

class Evaluation final {
public:
  int run(int argc, char *argv[]);
private:
  void evaluate(std::string imagePath);
private:
  static void printInvalid(const std::vector<std::string> &opts);
  static void printUsage(const po::options_description &desc);
};
