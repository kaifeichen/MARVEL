#include "run/wrapper/BackEndWrapper.h"
#include "lib/data/CameraModel.h"
#include "lib/data/Transform.h"
#include "lib/util/Utility.h"
#include "run/data/Session.h"
#include "run/event/DetectionEvent.h"
#include "run/event/FailureEvent.h"
#include "run/event/QueryEvent.h"
#include "run/wrapper/FrontEndWrapper.h"
#include <QCoreApplication>

BackEndWrapper::BackEndWrapper(const std::shared_ptr<Words> &words,
                               std::unique_ptr<Labels> &&labels, int sampleSize,
                               int corrSize, double distRatio)
    : _feature(sampleSize), _wordSearch(words), _dbSearch(words),
      _perspective(words, corrSize, distRatio), _visibility(std::move(labels)) {
}

bool BackEndWrapper::event(QEvent *event) {
  if (event->type() == QueryEvent::type()) {
    QueryEvent *queryEvent = static_cast<QueryEvent *>(event);
    std::unique_ptr<cv::Mat> image = queryEvent->takeImage();
    std::unique_ptr<CameraModel> camera = queryEvent->takeCameraModel();
    std::unique_ptr<Session> session = queryEvent->takeSession();

    std::unique_ptr<std::vector<std::string>> names(
        new std::vector<std::string>);
    bool success = identify(*image, *camera, *names, *session);

    if (success) {
      if (session->frontEndWrapper != nullptr) {
        FrontEndWrapper *frontEndWrapper = session->frontEndWrapper.get();
        QCoreApplication::postEvent(
            frontEndWrapper,
            new DetectionEvent(std::move(names), std::move(session)));
        std::cerr << "DEBUG: post detection event done " << std::endl;
      }
    } else {
      if (session->frontEndWrapper != nullptr) {
        FrontEndWrapper *frontEndWrapper = session->frontEndWrapper.get();
        QCoreApplication::postEvent(frontEndWrapper,
                                    new FailureEvent(std::move(session)));
      }
    }
    return true;
  }
  return QObject::event(event);
}

bool BackEndWrapper::identify(const cv::Mat &image, const CameraModel &camera,
                              std::vector<std::string> &names,
                              Session &session) {
  // feature extraction
  std::vector<cv::KeyPoint> keyPoints;
  cv::Mat descriptors;
  session.featuresStart = Utility::getTime();
  _feature.extract(image, keyPoints, descriptors);
  session.featuresEnd = Utility::getTime();

  // word search
  session.wordSearchStart = Utility::getTime();
  std::vector<int> wordIds = _wordSearch.search(descriptors);
  session.wordSearchEnd = Utility::getTime();

  // db search
  session.dbSearchStart = Utility::getTime();
  int dbId = _dbSearch.search(wordIds);
  session.dbSearchEnd = Utility::getTime();

  // PnP
  Transform pose;
  session.perspectiveStart = Utility::getTime();
  _perspective.localize(wordIds, keyPoints, descriptors, camera, dbId, pose);
  session.perspectiveEnd = Utility::getTime();

  if (pose.isNull()) {
    session.visibilityStart = 1;
    session.visibilityEnd = 0;
    return false;
  }

  // visibility
  session.visibilityStart = Utility::getTime();
  names = _visibility.process(dbId, camera, pose);
  session.visibilityEnd = Utility::getTime();

  return true;
}
