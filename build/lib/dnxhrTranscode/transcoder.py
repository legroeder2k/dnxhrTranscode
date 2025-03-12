import argparse
import os
from subprocess import Popen

from dnxhrTranscode.videoInformation import VideoInformation

def transcodeFile(inputfile, callargs):
    # Is our input path absolute or relative?
    if not os.path.isabs(inputfile):
        inputfile = os.path.abspath(inputfile)


    # Get the video information
    video_info = VideoInformation.getVideoInformation(inputfile)
    if video_info is None:
        print(f'Error getting video information for {inputfile}')
        return

    print(f'Transcoding {inputfile}: {video_info.getWidth()}x{video_info.getHeight()}@{video_info.getFramerate()}fps ...')

    # Create the output file name
    output_file_name = os.path.splitext(os.path.basename(inputfile))[0] + '.mov'
    output_file = os.path.join(callargs.output, output_file_name)

    if os.path.exists(output_file):
        print(f'Output file {output_file} already exists. Skipping...')
        return

    # Select our DNxHR format depending on the profile
    if callargs.profile == 'lb' or callargs.profile == 'sq' or callargs.profile == 'hq':
        format = "yuv422p"
    elif callargs.profile == 'hqx':
        if callargs.bit_depth == 12:
            format = "yuv422p12le"
        else:
            format = "yuv422p10le"
    elif callargs.profile == '444':
        if callargs.bit_depth == 12:
            format = "yuv444p12le"
        else:
            format = "yuv444p10le"

    profile = f'dnxhr_{callargs.profile}'

    print(f'Output file: {output_file} - Profile: {profile} - Format: {format}')

    commandCall = (f"ffmpeg -i \"{inputfile}\" -c:v dnxhd -vf \"scale={video_info.getWidth()}:{video_info.getHeight()},fps={video_info.getFramerate()}/1,format={format}\""
                   f" -profile:v {profile} -c:a pcm_s16le -ar 48000")

    if video_info.creation_date is not None:
        commandCall += f" -metadata creation_time=\"{video_info.creation_date}\""

    commandCall += f" \"{output_file}\""

    p1 = Popen(commandCall, shell=True)
    p1.wait()



def main():
    parser = argparse.ArgumentParser(description='Batch transcode video files to DNxHR using FFmpeg')
    parser.add_argument('-i', '--input', help='Input file or directory', required=True)
    parser.add_argument('-o', '--output', help='Output directory', required=True)
    parser.add_argument('-p', '--profile', help='DNxHR profile', default='hq', choices=['lb', 'sq', 'hq', 'hqx', '444'])
    parser.add_argument('-b', '--bit-depth', help='Bit depth for the DNxHR codec', default=8, choices=[8, 10, 12])

    args = parser.parse_args()

    # Is the input a file or a directory?
    # If it is a file, we will transcode it
    # If it is a directory, we will transcode all the files in it
    if os.path.isfile(args.input):
        transcodeFile(args.input, args)
    elif os.path.isdir(args.input):
        for file in os.listdir(args.input):
            transcodeFile(os.path.join(args.input, file), args)


if __name__ == '__main__':
    main()