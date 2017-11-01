#include "evaluation/Evaluation.h"
#include <opencv2/opencv.hpp>

int Evaluation::run(int argc, char *argv[]) {
  std::string imagePath;
  po::options_description visible("command options");
  visible.add_options() // use comment to force new line using formater
      ("help,h", "print help message");
  po::options_description hidden;
  hidden.add_options() // use comment to force new line using formater
      ("dbfile", po::value<std::string>(&imagePath)->required(), "database file");
  po::options_description all;
  all.add(visible).add(hidden);

  po::positional_options_description pos;
  pos.add("dbfile", 1);

  po::variables_map vm;
  po::parsed_options parsed = po::command_line_parser(argc, argv)
                                  .options(all)
                                  .positional(pos)
                                  .allow_unregistered()
                                  .run();
  po::store(parsed, vm);
  // print invalid options
  std::vector<std::string> unrecog =
      collect_unrecognized(parsed.options, po::exclude_positional);
  if (unrecog.size() > 0) {
      printInvalid(unrecog);
      printUsage(visible);
      return 1;
  }
  if (vm.count("help")) {
      printUsage(visible);
      return 0;
  }
  // check whether required options exist after handling help
  po::notify(vm);

  evaluate(imagePath);
  return 0;
}


void Evaluation::printInvalid(const std::vector<std::string> &opts) {
  std::cerr << "invalid options: ";
  for (const auto &opt : opts) {
    std::cerr << opt << " ";
  }
  std::cerr << std::endl;
}

void Evaluation::printUsage(const po::options_description &desc) {
  std::cout << "snaplink measure [command options] redBlueCircleImage" << std::endl
            << std::endl
            << desc << std::endl;
}

void Evaluation::evaluate(std::string imagePath) {
  cv::Mat bgr_image;
  bgr_image = cv::imread(imagePath, CV_LOAD_IMAGE_COLOR);   // Read the file
  if(!bgr_image.data) {                                 // Check for invalid input
    std::cout <<  "Could not open or find the image" << std::endl ;
    return;
  }
  cv::Mat orig_image = bgr_image.clone();
  cv::medianBlur(bgr_image, bgr_image, 3);
  // Convert input image to HSV
  cv::Mat hsv_image;
  cv::cvtColor(bgr_image, hsv_image, cv::COLOR_BGR2HSV);
  // Threshold the HSV image, keep only the red pixels
  cv::Mat lower_red_hue_range;
  cv::Mat upper_red_hue_range;
  cv::inRange(hsv_image, cv::Scalar(0, 100, 100), cv::Scalar(10, 255, 255), lower_red_hue_range);
  cv::inRange(hsv_image, cv::Scalar(160, 100, 100), cv::Scalar(179, 255, 255), upper_red_hue_range);
  // Combine the above two images
  cv::Mat red_hue_image;
  cv::addWeighted(lower_red_hue_range, 1.0, upper_red_hue_range, 1.0, 0.0, red_hue_image);
  cv::GaussianBlur(red_hue_image, red_hue_image, cv::Size(9, 9), 2, 2);
  //cv::imwrite("red.jpg", red_hue_image);
  // Use the Hough transform to detect circles in the combined threshold image
  std::vector<cv::Vec3f> circles;
  cv::HoughCircles(red_hue_image, circles, CV_HOUGH_GRADIENT, 1, red_hue_image.rows/8, 100, 20, 0, 0);
  // Loop over all detected circles and outline them on the original image
  if(circles.size() == 0) std::exit(-1);
  for(size_t current_circle = 0; current_circle < circles.size(); ++current_circle) {
    cv::Point center(std::round(circles[current_circle][0]), std::round(circles[current_circle][1]));
    int radius = std::round(circles[current_circle][2]);
    cv::circle(orig_image, center, radius, cv::Scalar(0, 255, 0), 5);
  }
  // Show images
  cv::imwrite("tli.jpg", lower_red_hue_range);
  cv::imwrite("tui.jpg", upper_red_hue_range);
  cv::imwrite("cti.jpg", red_hue_image);
  cv::imwrite("circle.jpg", orig_image);
}

