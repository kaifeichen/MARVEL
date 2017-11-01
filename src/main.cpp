#include "label/Labeler.h"
#include "measure/Measure.h"
#include "evaluation/Evaluation.h"
#include "run/Run.h"
#include "vis/Visualizer.h"
#include <boost/program_options.hpp>
#include <iostream>

#define VERSION "0.1"

namespace po = boost::program_options;

static void printInvalid(const std::vector<std::string> &opts);
static void printUsage(const po::options_description &desc);

int main(int argc, char *argv[]) {
  if (argc > 1) {
    if (std::string(argv[1]) == "run") {
      Run run;
      return run.run(argc - 1, argv + 1);
    } else if (std::string(argv[1]) == "vis") {
      Visualizer visualizer;
      return visualizer.run(argc - 1, argv + 1);
    } else if (std::string(argv[1]) == "label") {
      Labeler labeler;
      return labeler.run(argc - 1, argv + 1);
    } else if (std::string(argv[1]) == "measure") {
      Measure measure;
      return measure.run(argc - 1, argv + 1);
    } else if (std::string(argv[1]) == "evaluate") {
      Evaluation evaluation;
      return evaluation.run(argc-1, argv + 1);
    }
  }

  po::options_description global("global options");
  global.add_options() // use comment to force new line using formater
      ("help,h", "print help message") //
      ("version", "print version number");

  po::variables_map vm;
  po::parsed_options parsed = po::command_line_parser(argc, argv)
                                  .options(global)
                                  .allow_unregistered()
                                  .run();
  po::store(parsed, vm);

  // print invalid options
  std::vector<std::string> unrecog =
      collect_unrecognized(parsed.options, po::exclude_positional);
  if (unrecog.size() > 0) {
    printInvalid(unrecog);
    printUsage(global);
    return 1;
  }

  if (vm.count("help")) {
    printUsage(global);
    return 0;
  }

  // check whether required options exist after handling help
  po::notify(vm);
  if (vm.count("version")) {
    std::cout << "snaplink version " << VERSION << std::endl;
    return 0;
  }

  std::cout << global << std::endl;
  return 1;
}

static void printInvalid(const std::vector<std::string> &opts) {
  std::cerr << "invalid options: ";
  for (const auto &opt : opts) {
    std::cerr << opt << " ";
  }
  std::cerr << std::endl;
}

static void printUsage(const po::options_description &desc) {
  std::cout << "snaplink [global options] command [command options]"
            << std::endl
            << std::endl
            << desc << std::endl
            << "commands:" << std::endl
            << "  run        run snaplink" << std::endl
            << "  vis        visualize a datobase" << std::endl
            << "  measure    measure 2 points distance in a database" << std::endl
            << "  evaluate   evaluate performance from a image with red and blue dot on it" << std::endl
            << "  label      label a database" << std::endl;
}
