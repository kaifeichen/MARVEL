#pragma once

#include <rtabmap/core/Parameters.h>
#include <rtabmap/core/SensorData.h>
#include <rtabmap/core/Signature.h>
#include <rtabmap/core/Link.h>
#include <rtabmap/core/Features2d.h>
#include <rtabmap/utilite/UStl.h>
#include <typeinfo>
#include <list>
#include <map>
#include <set>
#include <opencv2/core/core.hpp>
#include <opencv2/features2d/features2d.hpp>
#include "WordsKdTree.h"

class WordsKdTree;

class MemoryLoc
{
public:
    static const int kIdStart;

public:
    MemoryLoc();
    virtual ~MemoryLoc();

    bool init(std::vector<std::string> &dbUrls,
              const rtabmap::ParametersMap &parameters = rtabmap::ParametersMap());
    const rtabmap::Signature *createSignature(rtabmap::SensorData &data, void *context);
    void close();

    rtabmap::Signature *getSignature(int dbId, int sigId) const;
    const std::vector< std::pair<cv::Point3f, std::string> > &getLabels(int dbId) const;
    const std::map<int, rtabmap::Signature *> &getSignatureMap(int dbId) const;
    const std::vector<std::map<int, rtabmap::Signature *> > &getSignatureMaps() const;

private:
    virtual void parseParameters(const rtabmap::ParametersMap &parameters);
    void optimizePoses(int dbId);  // optimize poses using TORO graph
    std::vector< std::pair<cv::Point3f, std::string> > readLabels(int dbId, std::string dbUrl) const;
    bool getPoint3World(int dbId, int imageId, int x, int y, pcl::PointXYZ &pWorld) const;

    std::map<int, int> getNeighborsId(
        int dbId,
        int signatureId,
        bool incrementMarginOnLoop = false,
        bool ignoreLoopIds = false,
        bool ignoreIntermediateNodes = false) const;
    std::map<int, rtabmap::Link> getNeighborLinks(int dbId, int sigId) const;
    void getMetricConstraints(
        int dbId,
        const std::set<int> &ids,
        std::map<int, rtabmap::Transform> &poses,
        std::multimap<int, rtabmap::Link> &links);

    void removeVirtualLinks(int signatureId);

    int getNextId();
    void clear();

private:
    // parameters
    rtabmap::ParametersMap parameters_;

    std::vector< std::map<int, int> > _sigIdMaps; // maps of ids of DB signatures and mem signatures
    std::vector< std::map<int, int> > _wordIdMaps; // maps of ids of DB words and mem words
    std::vector< std::map<int, rtabmap::Signature *> > _signatureMaps;

    std::vector< std::vector< std::pair<cv::Point3f, std::string> > > _labels;

    //Keypoint stuff
    WordsKdTree *_words;
    rtabmap::Feature2D *_feature2D;
};