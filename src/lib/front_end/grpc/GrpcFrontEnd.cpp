#include "lib/front_end/grpc/GrpcFrontEnd.h"
#include "lib/data/CameraModel.h"
#include <opencv2/core/core.hpp>
#include <opencv2/opencv.hpp>
#include <string>

const std::string GrpcFrontEnd::none = "None";

GrpcFrontEnd::GrpcFrontEnd(int grpcServerAddr, unsigned int maxClients) {
  _numClients = 0;
  _serverAddress = std::to_string(grpcServerAddr);
  _maxClients = maxClients;
}

GrpcFrontEnd::~GrpcFrontEnd() {
  std::cerr << "GrpcFrontEnd destructor" << std::endl;
  stop();
}

bool GrpcFrontEnd::start() {
  std::cerr << "DEBUG: Grpc start()" << std::endl;
  moveToThread(&_thread);
  connect(&_thread, &QThread::started, this, &GrpcFrontEnd::run);
  _thread.start();
  return true;
}

void GrpcFrontEnd::run() {
  std::string server_address(_serverAddress);

  grpc::ServerBuilder builder;
  // Listen on the given address without any authentication mechanism.
  builder.AddListeningPort("0.0.0.0:" + server_address,
                           grpc::InsecureServerCredentials());
  // Register "service" as the instance through which we'll communicate with
  // clients. In this case it corresponds to an *synchronous* service.
  builder.RegisterService(this);
  // Finally assemble the server.
  std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
  std::cout << "Server listening on " << server_address << std::endl;

  // Wait for the server to shutdown. Note that some other thread must be
  // responsible for shutting down the server for this call to ever return.
  server->Wait();
}

void GrpcFrontEnd::stop() {
  _numClients = 0;
  _serverAddress = "";
  _maxClients = 0;
}

grpc::Status GrpcFrontEnd::localize(
    grpc::ServerContext *context,
    grpc::ServerReaderWriter<snaplink_grpc::LocalizationResponse,
                             snaplink_grpc::LocalizationRequest> *stream) {
  (void)context; // ignore that variable without causing warnings

  {
    std::lock_guard<std::mutex> lock(_mutex);
    if (_numClients >= _maxClients) {
      return grpc::Status::CANCELLED;
    } else {
      _numClients++;
    }
  }

  snaplink_grpc::LocalizationRequest request;
  while (stream->Read(&request)) {
    snaplink_grpc::LocalizationResponse response;
    if(request.request_id_size() == 0) {
      continue; 
    }
    response.set_request_id(request.request_id(0));
    response.set_success(false);
    int numOfImages = request.image_size();
    std::vector<cv::Mat> images;
    std::vector<cv::Mat> poses;
    std::cout<<"step 1\n";
    for(int i = 0; i < numOfImages; i++) {
    std::cout<<"step 2\n";
      std::vector<uchar> data_i(request.image(i).begin(), request.image(i).end());
    std::cout<<"step 3\n";
      cv::Mat image_i = imdecode(cv::Mat(data_i, false), cv::IMREAD_GRAYSCALE);
    std::cout<<"step 4\n";
      images.push_back(image_i);
    std::cout<<"step 5\n";
      cv::Mat pose_i = cv::Mat::eye(3, 4, CV_64FC1); 
    std::cout<<"step 6\n";
      pose_i.at<double>(0, 0) = request.poses(i).data(0);
      pose_i.at<double>(0, 1) = request.poses(i).data(1);
      pose_i.at<double>(0, 2) = request.poses(i).data(2);
      pose_i.at<double>(0, 3) = request.poses(i).data(3);
      pose_i.at<double>(1, 0) = request.poses(i).data(4);
      pose_i.at<double>(1, 1) = request.poses(i).data(5);
      pose_i.at<double>(1, 2) = request.poses(i).data(6);
      pose_i.at<double>(1, 3) = request.poses(i).data(7);
      pose_i.at<double>(2, 0) = request.poses(i).data(8);
      pose_i.at<double>(2, 1) = request.poses(i).data(9);
      pose_i.at<double>(2, 2) = request.poses(i).data(10);
      pose_i.at<double>(2, 3) = request.poses(i).data(11);
    std::cout<<"step 7\n";
      std::cout<<pose_i<<std::endl;
    std::cout<<"step 8\n";
      poses.push_back(pose_i);
      //cv::imwrite(std::to_string(i)+ "_"+ std::to_string((int)request.blurness(i)) + ".jpg", image_i);
    std::cout<<"step 9\n";
    }

    std::vector<uchar> data(request.image(0).begin(), request.image(0).end());

    bool copyData = false;
    cv::Mat image = imdecode(cv::Mat(data, copyData), cv::IMREAD_GRAYSCALE);
    if (image.empty() || image.type() != CV_8U || image.channels() != 1) {
      stream->Write(response);
      continue;
    }

    // TODO add orientation into JPEG, so we don't need to rotate ourselves
    image = rotateImage(image, request.orientation(0));
    imwrite("imageRotated.jpg", image);
    int width = image.cols;
    int height = image.rows;
    response.set_width0(width);
    response.set_height0(height);
    float fx = request.camera().fx();
    float fy = request.camera().fy();
    float cx = request.camera().cx();
    float cy = request.camera().cy();
    updateIntrinsics(width, height, request.orientation(0), cx, cy);
    std::cout << "Width = " << width << ", Height = " << height
              << " Cx = " << cx << " Cy = " << cy << std::endl;
    CameraModel camera("", fx, fy, cx, cy, cv::Size(width, height));
    std::vector<FoundItem> items;
    std::pair<int, Transform>result = localizeFunc()(image, camera, &items);

    int dbId = result.first;
    Transform pose = result.second;
    if (pose.isNull()) {
      stream->Write(response);
      continue;
    }

    response.set_db_id(dbId);
    response.set_success(true);
    response.mutable_pose()->set_cols(4);
    response.mutable_pose()->set_rows(3);
    for (unsigned int i = 0; i < 12; i++) {
      response.mutable_pose()->add_data(pose.data()[i]);
    }

    // items are for test purpose only
    for (unsigned int i = 0; i < items.size(); i++) {
      snaplink_grpc::Item *item = response.add_items();
      item->set_name(items[i].name());
      item->set_x(items[i].x());
      item->set_y(items[i].y());
      item->set_size(items[i].size());
    }
    response.set_width(width > height ? height : width);
    response.set_height(width > height ? width : height);

    stream->Write(response);
  }

  {
    std::lock_guard<std::mutex> lock(_mutex);
    _numClients--;
  }

  return grpc::Status::OK;
}

grpc::Status
GrpcFrontEnd::getLabels(grpc::ServerContext *context,
                        const snaplink_grpc::Empty *empty,
                        snaplink_grpc::GetLabelsResponse *response) {
  (void)context; // avoid causing warnings
  (void)empty; // avoid causing warnings

  std::cout<<"getLabels triggered\n";
  // TODO cache this
  std::map<int, std::vector<Label>> labelsMap = getLabelsFunc()();
  auto &map = *response->mutable_labels_map();
  for (const auto &labels : labelsMap) {
    int dbId = labels.first;
    map[dbId] = snaplink_grpc::Labels();
    for (const auto &label : labels.second) {
      snaplink_grpc::Label *newLabel = map[dbId].add_labels();
      newLabel->set_db_id(label.getDbId());
      newLabel->set_x(label.getPoint3().x);
      newLabel->set_y(label.getPoint3().y);
      newLabel->set_z(label.getPoint3().z);
      newLabel->set_name(label.getName());
      std::cout<<"label name:" << label.getName() <<std::endl;
    }
  }
  std::cout<<response->labels_map_size()<<" is the size of the map\n";
  return grpc::Status::OK;
}

cv::Mat GrpcFrontEnd::rotateImage(cv::Mat img, int orientation) {
  if (orientation == 8) { // 90
    cv::transpose(img, img);
    cv::flip(img, img, 1);
  } else if (orientation == 3) { // 180
    cv::flip(img, img, -1);
  } else if (orientation == 6) { // 270
    cv::transpose(img, img);
    cv::flip(img, img, 0);
  }
  return img;
}

void GrpcFrontEnd::updateIntrinsics(int width, int height, int orientation,
                                    float &cx, float &cy) {
  float temp;
  if (orientation == 8) { // 90
    temp = cx;
    cx = width - cy;
    cy = temp;
  } else if (orientation == 3) { // 180
    cx = width - cx;
    cy = height - cy;
  } else if (orientation == 6) { // 270
    temp = cx;
    cx = cy;
    cy = height - temp;
  }
}
