import json
import os
import cv2
import moviepy.editor as mp
import shutil


"""
For video:


1. covert each video in each game(gameid) to pictures based on 5fps, and save info into json file 
   named test/train_info
2. each video has its own ori path and save path in the info json file

# source json file,and load corresponding information
"Player100000": {"Source": ".../VG_NBA_2024/20221107-Cleveland Cavaliers-Los Angeles Clippers/193", 
"Source_ID": "Video100000", "GameID": "20221107-Cleveland Cavaliers-Los Angeles Clippers", 
"Source_info": {"20221107-Cleveland Cavaliers-Los Angeles Clippers": {"img_size": [1280, 720, 3], "img_num": 750, "st_time": 5, "ed_time": 8.8, 
"Caption": "Defensive rebound by E.Mobley", "bbox": {"E.Mobley": [[692, 409, 799, 619], [708, 390, 798, 617], [705, 255, 791, 570], [700, 250, 801, 538], [730, 304, 800, 547], [724, 341, 832, 554], [737, 334, 853, 541], [745, 291, 846, 534], [730, 289, 846, 532], [712, 312, 880, 531], [701, 307, 852, 520], [682, 279, 840, 518], [685, 280, 808, 512], [658, 271, 824, 503], [670, 278, 779, 501], [652, 261, 840, 489], [0, 0, 0, 0], [692, 251, 855, 487], [737, 263, 854, 497], [757, 244, 916, 488], [0, 0, 0, 0]]}}}, 
"BBox": [[692, 409, 799, 619], [708, 390, 798, 617], [705, 255, 791, 570], [700, 250, 801, 538], [730, 304, 800, 547], [724, 341, 832, 554], [737, 334, 853, 541], [745, 291, 846, 534], [730, 289, 846, 532], [712, 312, 880, 531], [701, 307, 852, 520], [682, 279, 840, 518], [685, 280, 808, 512], [658, 271, 824, 503], [670, 278, 779, 501], [652, 261, 840, 489], [0, 0, 0, 0], [692, 251, 855, 487], [737, 263, 854, 497], [757, 244, 916, 488], [0, 0, 0, 0]], 
"Label": "E.Mobley", "Sequence_path": ".../Players/Player100000"}

save format:
{"video_id":}
"""


# extract video segmentation based on its json file (start_time and end_time)
def extract_video_segment(input_video_path, output_video_path, start_time, end_time):

    if not os.path.exists(output_video_path):
        os.makedirs(output_video_path)
    num = input_video_path.split("/")[-1]
    file_video = num + ".mp4"
    input_video_path = os.path.join(input_video_path, file_video)
    video = mp.VideoFileClip(input_video_path).subclip(start_time, end_time)
    save_path = os.path.join(output_video_path, "out.mp4")
    #video.write_videofile(save_path, audio=True, codec="mpeg4")
    video.write_videofile(save_path, audio=True, codec=None)

# convert video to pictures
def extract_frames(video_path, output_folder, fps=5):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    video_path = os.path.join(video_path, "out.mp4")
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return

    # Get the original FPS of the video
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(original_fps // fps)

    frame_count = 0
    saved_frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_name = f"{saved_frame_count:06d}.jpg"
            cv2.imwrite(os.path.join(output_folder, frame_name), frame)
            saved_frame_count += 1

        frame_count += 1

    cap.release()

# prepare to use
test_game_list = ["20221107-Brooklyn Nets-Dallas Mavericks",
                  "20221107-Cleveland Cavaliers-Los Angeles Clippers",
                  "20221107-Denver Nuggets-San Antonio Spurs",
                  "20230402-Washington Wizards-New York Knicks",
                  "20230404-Toronto Raptors-Charlotte Hornets"]
# test video json
test_video_dict = {}
test_video_file = open('./test_video_info.json', mode='a', encoding='utf-8')
#test_player_dict = {}

# save test pictures
test_path = "/home/xzy/NBA/VG_NBA_data/"

# save video segmentation, after will delete
test_video_path = "/home/xzy/NBA/VG_NBA_linshi/"

# load ori PlayerID_bbox_sequences_info file
with open("/home/xzy/NBA/LLM_VC/Player_identify/Save/C_PlayerID_bbox_sequences_info.json", encoding='utf-8') as Video_f:
    result_info = json.load(Video_f)


# iterate through the dictionary  遍历字典
for k_vid, v_vid in result_info.items():
    game_id = v_vid["GameID"]  # {"source":..., "sequence_path":...}
    video_id = v_vid["Source_ID"]
    print("video_id", video_id)
    if game_id in test_game_list:
        if video_id not in test_video_dict:
            # extract video
            source_path = v_vid["Source"]
            print("source_path", source_path)  # to segment video

            caption = v_vid["Source_info"][game_id]["Caption"]

            # 基于起止时刻截取片段
            start_time = v_vid["Source_info"][game_id]["st_time"]
            end_time = v_vid["Source_info"][game_id]["ed_time"]
            video_save_path = os.path.join(test_video_path, game_id, video_id)
            extract_video_segment(source_path, video_save_path, start_time, end_time)
            # bbox = v_vid["BBox"]  # to extract player---train
            # 基于截取的片段分割成图像集  # Extract frames from the video
            pictures_path = os.path.join(test_path, video_id)  # out path
            extract_frames(video_save_path, pictures_path, fps=5)  # 截取图像集

            # delete video segment
            try:
                shutil.rmtree(video_save_path)
                #print(f"success remove the folder: {output_video_segment_path}")
            except OSError as e:
                pass
                #print(f"the error in delting the folder: {e.strerror}")

            # save json
            video_sub = test_video_dict[video_id] = {}
            video_sub["source_path"] = source_path
            video_sub["caption"] = caption
            video_sub["save_path"] = pictures_path
            video_sub["game_id"] = game_id
            #video_save_path = os.path.join(test_path, game_id, video_id)
        else:
            continue

json_save = json.dumps(test_video_dict, ensure_ascii=False)
test_video_file.write(json_save)
test_video_file.close()



