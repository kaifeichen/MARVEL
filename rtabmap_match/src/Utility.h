#pragma once

#include <rtabmap/core/Transform.h>

namespace rtabmap
{

class Utility
{
public:
    static bool compareCVPoint2f(cv::Point2f p1, cv::Point2f p2);
    static bool isInFrontOfCamera(const cv::Point3f &point, const Transform &P);
};

} /* namespace rtabmap */