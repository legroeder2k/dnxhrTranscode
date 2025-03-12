import subprocess
import json

class VideoInformation:
    width = 1920
    height = 1080
    framerate = 30
    color_profile = "yuv420p"
    creation_date = None

    def __init__(self, width, height, framerate, color_profile, creation_date = None):
        self.width = width
        self.height = height
        self.frameRate = framerate
        self.color_profile = color_profile
        self.creation_date = creation_date

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def getFramerate(self):
        return self.framerate

    def getColorprofile(self):
        return self.color_profile

    # static method to get the information from a video file using ffmpeg
    @staticmethod
    def getVideoInformation(videoFile):
        # We will use ffmpeg to get the information from the video file
        process = subprocess.Popen(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", videoFile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate();

        if process.returncode != 0:
            print(f'Error getting video information: {err}')
            return None

        # Parse the JSON output
        jsonOutput = json.loads(out)

        # Find the video stream
        videoStream = None
        for stream in jsonOutput['streams']:
            if stream['codec_type'] == 'video':
                videoStream = stream
                break

        if videoStream is None:
            print('No video stream found')
            return None

        # Get the resolution
        resolutionW = int(videoStream['width'])
        resolutionH = int(videoStream['height'])
        frameRate = int(videoStream['r_frame_rate'].split('/')[0])
        colorProfile = videoStream['pix_fmt']

        if 'tags' in jsonOutput['format']:
            if 'com.apple.quicktime.creationdate' in jsonOutput['format']['tags']:
                creationDate = jsonOutput['format']['tags']['com.apple.quicktime.creationdate']
            elif 'creation_time' in jsonOutput['format']['tags']:
                creationDate = jsonOutput['format']['tags']['creation_time']
            else:
                creationDate = None

        # check to see if we have rotation metadata
        if 'side_data_list' in videoStream:
            for sideData in videoStream['side_data_list']:
                if 'rotation' in sideData:
                    rotation = sideData['rotation']
                    if rotation == 90 or rotation == 270 or rotation == -90 or rotation == -270:
                        # swap width and height
                        resolutionH, resolutionW = resolutionW, resolutionH

        return VideoInformation(resolutionW, resolutionH, frameRate, colorProfile, creationDate)