#pragma once

#include <rtabmap/core/VisualWord.h>
#include <vector>
#include <map>

class Words
{
public:
    /**
     * Add words, ownership transfer
     */
    virtual void addWords(const std::vector<rtabmap::VisualWord *> &words) = 0;

    /**
     * get all words
     */
    virtual const std::map<int, rtabmap::VisualWord *> &getWords() const = 0;

    /**
     * find the indices of the nearst neighbors of descriptors
     */
    virtual std::vector<int> findNN(const cv::Mat &descriptors) const = 0;

    /**
     * clear all words 
     */
    virtual void clear() = 0;
};
