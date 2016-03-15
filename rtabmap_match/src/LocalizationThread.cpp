#include <rtabmap/utilite/ULogger.h>

#include "LocalizationThread.h"
#include "ImageEvent.h"
#include "LocationEvent.h"

LocalizationThread::LocalizationThread(Localization *loc, unsigned int dataBufferMaxSize) :
    _loc(loc),
    _dataBufferMaxSize(dataBufferMaxSize)
{
    UASSERT(_loc != NULL);
}

LocalizationThread::~LocalizationThread()
{
    this->unregisterFromEventsManager();
    this->join(true);
    if (_loc)
    {
        delete _loc;
    }
}

void LocalizationThread::handleEvent(UEvent *event)
{
    if (this->isRunning())
    {
        if (event->getClassName().compare("ImageEvent") == 0)
        {
            ImageEvent *imageEvent = (ImageEvent *)event;
            this->addData(imageEvent->data(), imageEvent->context());
        }
    }
}

void LocalizationThread::mainLoopKill()
{
    _dataAdded.release();
}

void LocalizationThread::mainLoop()
{
    rtabmap::SensorData data;
    void *context = NULL;
    if (getData(data, context))
    {
        rtabmap::Transform pose = _loc->localize(data);
        // a null pose notify that loc could not be computed
        this->post(new LocationEvent(data, pose, context));
    }
}

void LocalizationThread::addData(const rtabmap::SensorData &data, void *context)
{
    if (data.imageRaw().empty() || (data.cameraModels().size() == 0 && !data.stereoCameraModel().isValidForProjection()))
    {
        ULOGGER_ERROR("Missing some information (image empty or missing calibration)!?");
        return;
    }

    bool notify = true;
    _dataMutex.lock();
    {
        _dataBuffer.push_back(data);
        _contextBuffer.push_back(context);

        while (_dataBufferMaxSize > 0 && _dataBuffer.size() > _dataBufferMaxSize)
        {
            UWARN("Data buffer is full, the oldest data is removed to add the new one.");
            _dataBuffer.pop_front();
            _contextBuffer.pop_front();
            notify = false;
        }
    }
    _dataMutex.unlock();

    if (notify)
    {
        _dataAdded.release();
    }
}

bool LocalizationThread::getData(rtabmap::SensorData &data, void *&context)
{
    bool dataFilled = false;
    _dataAdded.acquire();
    _dataMutex.lock();
    {
        if (!_dataBuffer.empty() && _dataBuffer.size() == _contextBuffer.size())
        {
            data = _dataBuffer.front();
            context = _contextBuffer.front();
            _dataBuffer.pop_front();
            _contextBuffer.pop_front();
            dataFilled = true;
        }
    }
    _dataMutex.unlock();
    return dataFilled;
}
