# this file is to fetch the data from the database and create a csv
import pandas
from datetime import *
from tunnelfunctions import *
# this function calculates an array for all the cameras and averages
# the animal count over the whole dataset that has been selected
# return is an array of integer
# takes the filepath, a starttime, an endtime and the amount of cameras
# the amount of cameras is mostly set and in HTML hardcoded,
# but since this is python i can do what the fuck i want


def getAverageOverTimeByCamera(path, stime, etime, cams, df2, csv=False):
    AverageOverTime = []
    if csv:
        # data for the database, which colums will be read
        df = pandas.read_csv(path,
                             usecols=['camera', 'objectCount', 'timestamp'],
                             parse_dates=['timestamp'])

        # first filter, get the timestamp from begin to end and just use this data from now on
        wholetimeframe = df[(df['timestamp'] >= str(stime))
                            & (df['timestamp'] <= str(etime))]
    else:
        wholetimeframe = df2
    # this is just the column 'objectCount'
    # this is the sum and the size of the whole 'object Count' dataframe
    # we have 12 cameras, therefor the for loop
    for i in range(1, cams + 1):
        # get just the columns that include that camera, so delete all other columns
        cam1timeframe = wholetimeframe[wholetimeframe.camera == i]
        # as long as the retreived dataframe isnt empty
        if not cam1timeframe.empty:
            # add up all the numbers in the 'objectCount' column
            # get the array of the individual Camera, take just the 'objectCount' column and sum all these values up
            AverageOverTime.append(int(cam1timeframe.objectCount.sum() /
                                       cam1timeframe.objectCount.size))
        # if the retrieved column has no data (=0), the dataframe returns None
        else:
            # so here im writing 0 in the array
            AverageOverTime.append(0)
    # return the array of all these cams
    # print(camtimes)
    return AverageOverTime

# this function calculates the limits of a file that is being fed to it
# output is an 2x1 array that hols a start date and an end date as a string


def maxDate(path, df2, csv=False):
    if csv:
        # data for the database, which colums will be read
        df = pandas.read_csv(path,
                             usecols=['camera', 'objectCount', 'timestamp'])
        # get the minimum date from the first row, and the one from the last
        # the last will be determined by the size of the dataset - 1, since we start at 0
    else:
        df = df2
        print('I will use the provided dataset')
    return [df.loc[0, 'timestamp'],
                df.loc[df.timestamp.size - 1, 'timestamp']
                ]

# this function returns the amount of measured points in a csv file
# for one camera
# honestly no clue why i wrote this, it was probably 4am


def fetchCameras(path, cam):
    df = pandas.read_csv(path,
                         usecols=['camera', 'objectCount',
                                  'objectBoxes', 'timestamp'],
                         parse_dates=['timestamp'])

    return (df[df.camera == cam]).size


def getVideoFiles(path, stime, etime, cams):
    videoFiles = []
    # get the whole timeframe, with all the videofiles
    df = pandas.read_csv(path,
                         usecols=['camera',
                                  'timestamp',
                                  'videoFilename'],
                         parse_dates=['timestamp'])
    # first filter, get the timestamp from begin to end and just use this data from now on
    wholetimeframe = df[(df['timestamp'] >= str(stime))
                        & (df['timestamp'] <= str(etime))]
    for i in range(1, cams + 1):
        cam1timeframe = wholetimeframe[wholetimeframe.camera == i]
        for filename in cam1timeframe.videoFilename:
            videoFiles.append(filename)
            for filename2 in videoFiles:
                if filename2 != filename:
                    videoFiles.append(filename)

# function that returns the size of a dataset


def size(path):
    df = pandas.read_csv(path)
    return df.size
