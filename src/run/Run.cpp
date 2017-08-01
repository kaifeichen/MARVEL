#include "run/Run.h"
#include "lib/data/FoundItem.h"
#include "lib/data/Label.h"
#include "lib/data/Transform.h"
#include "lib/front_end/grpc/GrpcFrontEnd.h"
#include "lib/util/Utility.h"
#include "lib/visualize/visualize.h"
#include <QCoreApplication>
#include <QtConcurrent>
#include <cstdio>
#include <pthread.h>
#include <utility>
#include <zbar.h>
int Run::run(int argc, char *argv[]) {
  // Parse arguments

  po::options_description visible("command options");
  visible.add_options() // use comment to force new line using formater
      ("help,h", "print help message") //
      ("port,p", po::value<int>(&_port)->default_value(8080),
       "the port that GRPC front end binds to") //
      ("feature-limit,f", po::value<int>(&_featureLimit)->default_value(0),
       "limit the number of features used") //
      ("corr-limit,c", po::value<int>(&_corrLimit)->default_value(0),
       "limit the number of corresponding 2D-3D points used") //
      ("save-image,s", po::bool_switch(&_saveImage)->default_value(false),
       "save images to files, which can causes significant delays.") //
      ("tag-size, z", po::value<double>(&_tagSize)->default_value(0.16),
       "size of april-tags used in the room") //
      ("visualize,v", po::bool_switch(&_vis)->default_value(false),
       "Visualize the 3D model and localized camera pose") //
      ("dist-ratio,d", po::value<float>(&_distRatio)->default_value(0.7),
       "distance ratio used to create words");

  po::options_description hidden;
  hidden.add_options() // use comment to force new line using formater
      ("dbfiles", po::value<std::vector<std::string>>(&_dbFiles)
                      ->multitoken()
                      ->default_value(std::vector<std::string>(), ""),
       "database files");

  po::options_description all;
  all.add(visible).add(hidden);

  po::positional_options_description pos;
  pos.add("dbfiles", -1);

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
    Run::printInvalid(unrecog);
    Run::printUsage(visible);
    return 1;
  }

  if (vm.count("help")) {
    Run::printUsage(visible);
    return 0;
  }

  // check whether required options exist after handling help
  po::notify(vm);

  // Run the program
  QCoreApplication app(argc, argv);
  std::map<int, Word> words;
  std::map<int, Room> rooms;
  std::map<int, std::vector<Label>> labels;
  if (_dbFiles.size()) {
    _mode = Run::FULL_FUNCTIONING;
    std::cout << "READING DATABASES" << std::endl;
    _adapter = std::make_unique<RTABMapAdapter>(_distRatio);
    if (!_adapter->init(
            std::set<std::string>(_dbFiles.begin(), _dbFiles.end()))) {
      std::cerr << "reading data failed";
      return 1;
    }

   
    words = _adapter->getWords();
    rooms = _adapter->getRooms();
    labels = _adapter->getLabels();

    if(_vis) {
      _visualize = std::make_unique<Visualize>(_adapter->getImages());
      QtConcurrent::run(_visualize.get(), &Visualize::startVis);
    }
    
    std::cout << "RUNNING COMPUTING ELEMENTS" << std::endl;
    _feature = std::make_unique<Feature>(_featureLimit);
    _wordSearch = std::make_unique<WordSearch>(words);
    _roomSearch = std::make_unique<RoomSearch>(rooms, words);
    _perspective =
        std::make_unique<Perspective>(rooms, words, _corrLimit, _distRatio);
    _visibility = std::make_unique<Visibility>(labels);
    _aprilTag = std::make_unique<Apriltag>(_tagSize);
  } else {
    _mode = Run::QR_ONLY;
    std::cout << "Only QR identification is enabled" << std::endl;
  }

  std::unique_ptr<FrontEnd> frontEnd;
  std::cerr << "initializing GRPC front end" << std::endl;
  frontEnd = std::make_unique<GrpcFrontEnd>(_port, MAX_CLIENTS);
  if (frontEnd->start() == false) {
    std::cerr << "starting GRPC front end failed";
    return 1;
  }
  frontEnd->registerOnQuery(std::bind(
      &Run::identify, this, std::placeholders::_1, std::placeholders::_2));
  std::cout << "Initialization Done" << std::endl;

  return app.exec();
}



void Run::printInvalid(const std::vector<std::string> &opts) {
  std::cerr << "invalid options: ";
  for (const auto &opt : opts) {
    std::cerr << opt << " ";
  }
  std::cerr << std::endl;
}

void Run::printUsage(const po::options_description &desc) {
  std::cout << "cellmate run [command options] db_file..." << std::endl
            << std::endl
            << desc << std::endl;
}

void Run::printImageLocalTime(long total, long feature, long wordSearch, long roomSearch,
                    long perspective) {
  std::cout << "Time ImageLocalize  overall: " << total << " ms" << std::endl;
  std::cout << "Time feature: " << feature << " ms" << std::endl;
  std::cout << "Time wordSearch: " << wordSearch << " ms" << std::endl;
  std::cout << "Time roomSearch: " << roomSearch << " ms" << std::endl;
  std::cout << "Time perspective: " << perspective << " ms" << std::endl;
}

// must be thread safe
std::vector<FoundItem> Run::identify(const cv::Mat &image,
                                     const CameraModel &camera) {
  std::cout<<"**********************************New Query Image****************************************\n";
  std::vector<FoundItem> results;
  std::vector<FoundItem> qrResults;
  long startTime;
  long totalStartTime = Utility::getTime();

  std::vector<Transform> aprilTagPoses;
  std::vector<int> aprilTagCodes;

  std::pair<std::vector<int>, std::vector<Transform>> aprilDetectResult;
  std::pair<int, Transform> imageLocResultPose;

  QFuture<std::pair<std::vector<int>, std::vector<Transform>>> aprilDetectWatcher;
  QFuture<std::pair<int, Transform>> imageLocalizeWatcher;

  // qr extraction
  QFuture<bool> qrWatcher =
      QtConcurrent::run(this, &Run::qrExtract, image, &qrResults);

  if (_saveImage) {
    QtConcurrent::run(
        [=]() { imwrite(std::to_string(Utility::getTime()) + ".jpg", image); });
  }

  if (_mode == Run::FULL_FUNCTIONING && camera.isValid()) {
      // aprilTag extraction and localization
    aprilDetectWatcher = QtConcurrent::run(_aprilTag.get(), &Apriltag::aprilDetect, image, camera);

    imageLocalizeWatcher = QtConcurrent::run(this, &Run::imageLocalize, image, camera);

    aprilDetectResult = aprilDetectWatcher.result();

    //This lookup and localize part takes less than 1ms, so didn't put in another thread to run 
    std::vector<Transform> tagPoseInCamFrame = aprilDetectResult.second;
    std::vector<std::pair<int, Transform>>  tagPoseInModelFrame = _adapter->lookupAprilCodes(aprilDetectResult.first);
    std::vector<std::pair<int, Transform>> aprilResultPose = _aprilTag->aprilLocalize(tagPoseInCamFrame, tagPoseInModelFrame);

    imageLocResultPose = imageLocalizeWatcher.result();

    Transform finalPose;
    int roomId;
    // Select the final pose to use in vis from multiple pose candidates
    if(aprilResultPose.size() > 0) {
      finalPose = aprilResultPose[0].second;
      roomId = aprilResultPose[0].first;
    } else {
      finalPose = imageLocResultPose.second;
      roomId = imageLocResultPose.first;
    }

    if(_vis) {
      _visualize->setPose(roomId, finalPose);
    }
    
    if (finalPose.isNull()) {
      std::cerr << "image localization failed (did you provide the correct "
                   "intrinsic matrix?)"
                << std::endl;
    } else {
      // visibility
      long visibilityTime;
      {
        std::lock_guard<std::mutex> lock(_visibilityMutex);
        startTime = Utility::getTime();
        results = _visibility->process(roomId, camera, finalPose);
        visibilityTime = Utility::getTime() - startTime;
        std::cout << "Time visibility "<< visibilityTime << " ms" <<std::endl;
      }

    }
  } else {
    std::cerr << "image localization not performed." << std::endl;
  }

  if (qrWatcher.result()) {
    results.insert(results.begin(), qrResults.begin(), qrResults.end());
  }

  long totalTime = Utility::getTime() - totalStartTime;
  std::cout << "Time Identify overall " << totalTime << " ms" <<std::endl;
  
  if (aprilTagPoses.size() > 0 && !imageLocResultPose.second.isNull()) {
    QtConcurrent::run(this, &Run::calculateAndSaveAprilTagPose, aprilDetectResult.second,
                      aprilDetectResult.first, imageLocResultPose);
  }
  return results;
}

std::pair<int, Transform> Run::imageLocalize(const cv::Mat &image,
                                             const CameraModel &camera) {
  long totalStartTime = Utility::getTime();
  long startTime;
  // feature extraction
  std::vector<cv::KeyPoint> keyPoints;
  cv::Mat descriptors;
  long featureTime;
  {
    std::lock_guard<std::mutex> lock(_featureMutex);
    startTime = Utility::getTime();
    _feature->extract(image, keyPoints, descriptors);
    featureTime = Utility::getTime() - startTime;
  }

  // word search
  std::vector<int> wordIds;
  long wordSearchTime;
  {
    std::lock_guard<std::mutex> lock(_wordSearchMutex);
    startTime = Utility::getTime();
    wordIds = _wordSearch->search(descriptors);
    wordSearchTime = Utility::getTime() - startTime;
  }

  // room search
  int roomId;
  long roomSearchTime;
  {
    std::lock_guard<std::mutex> lock(_roomSearchMutex);
    startTime = Utility::getTime();
    roomId = _roomSearch->search(wordIds);
    roomSearchTime = Utility::getTime() - startTime;
  }

  // PnP
  Transform pose;
  long perspectiveTime;
  {
    std::lock_guard<std::mutex> lock(_perspectiveMutex);
    startTime = Utility::getTime();
    pose =
        _perspective->localize(wordIds, keyPoints, descriptors, camera, roomId);
    perspectiveTime = Utility::getTime() - startTime;
  }

  long totalTime = Utility::getTime() - totalStartTime;
  printImageLocalTime(totalTime, featureTime, wordSearchTime, roomSearchTime, perspectiveTime);
  return std::make_pair(roomId, pose);
}

bool Run::qrExtract(const cv::Mat &im, std::vector<FoundItem> *results) {
  long totalStartTime = Utility::getTime();
 
  std::cout << "Qr extracting\n";
  zbar::ImageScanner scanner;
  scanner.set_config(zbar::ZBAR_NONE, zbar::ZBAR_CFG_ENABLE, 1);
  uchar *raw = (uchar *)im.data;
  int width = im.cols;
  int height = im.rows;
  std::cout << "Widith = " << width << " Height = " << height << std::endl;
  zbar::Image image(width, height, "Y800", raw, width * height);

  int n = scanner.scan(image);
  std::cout << "n is " << n << std::endl;
  for (zbar::Image::SymbolIterator symbol = image.symbol_begin();
       symbol != image.symbol_end(); ++symbol) {
    std::cout << "decoded " << symbol->get_type_name() << " symbol "
              << symbol->get_data() << std::endl;
    // Zbar's coordinate system is topleft = (0,0)
    // x axis is pointing to right
    // y axis is pointing to bottom

    double x0 = symbol->get_location_x(0);
    double x1 = symbol->get_location_x(1);
    double x2 = symbol->get_location_x(2);
    double x3 = symbol->get_location_x(3);
    double y0 = symbol->get_location_y(0);
    double y1 = symbol->get_location_y(1);
    double y2 = symbol->get_location_y(2);
    double y3 = symbol->get_location_y(3);
    double meanX = (x0 + x1 + x2 + x3) / 4;
    double meanY = (y0 + y1 + y2 + y3) / 4;
    double size = (meanX - x0) > 0 ? (meanX - x0) : (x0 - meanX);
    FoundItem item(symbol->get_data(), meanX, meanY, size, width, height);
    std::cout << "Size is " << size << std::endl;
    std::cout << "X is " << meanX << std::endl;
    std::cout << "Y is " << meanY << std::endl;
    results->push_back(item);
  }

  long totalTime = Utility::getTime() - totalStartTime;
  std::cout << "Time QR extract overall " << totalTime << " ms" <<std::endl;
  
  return results->size() > 0;
}

// std::vector<std::pair<int, Transform>> Run::aprilLocalize(
//     const cv::Mat &im, const CameraModel &camera, double tagSize,
//     std::vector<Transform> *tagPoseInCamFrame, std::vector<int> *tagCodes) {
//   long totalStartTime = Utility::getTime();
//   long startTime;
  
//   std::vector<std::pair<int, Transform>> results;

//   TagDetectorParams params;
//   TagFamily family("Tag36h11");
//   TagDetector detector(family, params);
//   TagDetectionArray detections;

//   cv::Point2d opticalCenter;
//   opticalCenter.x = camera.cx();
//   opticalCenter.y = camera.cy();
  
//   long aprilDetectionTime;
//   startTime = Utility::getTime();
//   detector.process(im, opticalCenter, detections);
//   aprilDetectionTime =  Utility::getTime() - startTime;
//   std::cout <<"Time aprilDetection " << aprilDetectionTime << " ms" << std::endl;

//   cv::Mat rVec, t;
//   for (unsigned int i = 0; i < detections.size(); i++) {
//     CameraUtil::homographyToPoseCV(camera.fx(), camera.fy(), tagSize,
//                                    detections[i].homography, rVec, t);
//     cv::Mat r,dump;
//     cv::Rodrigues(rVec,r,dump);
//     Transform pose(r.at<double>(0, 0), r.at<double>(0, 1), r.at<double>(0, 2), t.at<double>(0, 0), //
//                    r.at<double>(1, 0), r.at<double>(1, 1), r.at<double>(1, 2), t.at<double>(0, 1), //
//                    r.at<double>(2, 0), r.at<double>(2, 1), r.at<double>(2, 2), t.at<double>(0, 2));
//     tagPoseInCamFrame->push_back(pose);
//     tagCodes->push_back(detections[i].code);

//     long aprilLookupTime;
//     startTime = Utility::getTime();
//     // pair<roomId, tagPoseInModelFrame>, roomId will be -1 if no such tag code
//     // exist in db
//     std::pair<int, Transform> tagPoseInModelFrame =
//         _adapter->lookupAprilCode(detections[i].code);
//     aprilLookupTime = Utility::getTime() - startTime;
//     std::cout <<"Time aprilLookup " << aprilLookupTime << " ms" << std::endl;
    
//     if (tagPoseInModelFrame.first >= 0) {
//       results.push_back(
//           std::make_pair(tagPoseInModelFrame.first,
//                          tagPoseInModelFrame.second * pose.inverse()));
//     }
//   }
//   long totalTime = Utility::getTime() - totalStartTime;
//   std::cout << "Time AprilLocalize overall " << totalTime << " ms" <<std::endl;
//   return results;
// }

void Run::calculateAndSaveAprilTagPose(
    std::vector<Transform> aprilTagPosesInCamFrame,
    std::vector<int> aprilTagCodes,
    std::pair<int, Transform> imageLocResultPose) {

  for (unsigned int i = 0; i < aprilTagPosesInCamFrame.size(); i++) {
    Transform tagPoseInCamFrame = aprilTagPosesInCamFrame[i];
    int code = aprilTagCodes[i];

    int roomId = imageLocResultPose.first;
    Transform camPoseInModelFrame = imageLocResultPose.second;
    Transform tagPoseInModelFrame = _aprilTag->calculateNewAprilTagPoseInModelFrame(camPoseInModelFrame, tagPoseInCamFrame);
    long time = Utility::getTime();
    _adapter->saveAprilTagPose(roomId, time, code, tagPoseInModelFrame);
  }
}
