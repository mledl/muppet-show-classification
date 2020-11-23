from moviepy.editor import *
import os
from pathlib import Path
from pydub import AudioSegment
from pydub.silence import split_on_silence

character_map = {0: 'kermit_the_frog',
                 1: 'waldorf_and_statler',
                 2: 'pig',
                 3: 'swedish_chef',
                 4: 'none'}


def extract_audio_from_video(video_path, audio_base_path):
    # extract audio from avi video
    print('[INFO] Start extracting wav from avi')
    filename = audio_base_path + os.path.basename(os.path.normpath(video_path)).split('.')[0] + '.wav'
    if not os.path.isfile(filename):
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(filename)
        video.close()
        print('[INFO] Finished extracting wav from avi')
    else:
        print('[INFO] Wav File already exists')


def extract_character_screentime(ground_truth_textfile):
    print('[INFO] Start calculating screen times for characters')
    screen_time_dict = {}
    for key in character_map:
        screen_time_dict[key] = screentime_per_class(ground_truth_textfile, key)

    print('[INFO] Finished calculating screen times for characters')
    return screen_time_dict


def screentime_per_class(ground_truth_textfile, class_label):
    with open(ground_truth_textfile) as file:
        lines = file.readlines()

    intervals = []
    in_interval = False
    interval_start_frame_id = -1
    interval_end_frame_id = -1
    for line in lines[1:]:
        splits = line.strip().split(',')
        frame_id = splits[0]
        labels = [int(splits[i]) for i in range(1, len(splits))]

        if class_label in labels:
            if in_interval is False:
                interval_start_frame_id = frame_id
                in_interval = True
        else:
            if in_interval is True:
                interval_end_frame_id = frame_id
                in_interval = False
                intervals.append((interval_start_frame_id, interval_end_frame_id))

    return intervals


def slice_audio_from_video(ground_truth_textfile, audio_path, audio_base_path, video_fps):
    screen_time_map = extract_character_screentime(ground_truth_textfile)
    audio = AudioSegment.from_wav(audio_path)

    print('[INFO] Start slicing audio files')
    for key, value in screen_time_map.items():
        print('[INFO] Start slicing for label: %d' % key)
        for i, interval in enumerate(value):
            start = (float(interval[0]) / video_fps) * 1000
            end = (float(interval[1]) / video_fps) * 1000
            audio_chunk = audio[start:end]
            # if key == 4:
            #     none_chunks = split_on_silence(audio_chunk, min_silence_len=1000, silence_thresh=-16)
            #     for j, none_chunk in enumerate(none_chunks):
            #         none_chunk.export(audio_base_path + '4_' + str(j) + '.wav', format='wav')
            # else:
            audio_chunk.export(audio_base_path + str(key) + '_' + str(i) + '.wav', format='wav')
        print('[INFO] Finished slicing for label: %d' % key)


if __name__ == '__main__':
    test_video_path = '../../videos/Muppets-02-01-01.avi'
    test_audio_base_path = '../../audio/'
    test_audio_path = test_audio_base_path + 'Muppets-02-01-01.wav'
    test_ground_truth_textfile = '../../ground_truth/Muppets-02-01-01/Muppets-02-01-01.txt'
    fps = 25

    Path(test_audio_base_path).mkdir(parents=True, exist_ok=True)
    extract_audio_from_video(video_path=test_video_path, audio_base_path=test_audio_base_path)
    slice_audio_from_video(ground_truth_textfile=test_ground_truth_textfile, audio_path=test_audio_path,
                           audio_base_path=test_audio_base_path, video_fps=fps)
    # os.remove(test_audio_path)