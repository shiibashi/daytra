from PIL import ImageGrab
from PIL import Image
from PIL import ImageDraw, ImageFont
import datetime
import numpy
import cv2
import time
import os
import pandas

import predict
import rl

SHAPE =(1000, 810)
FPS = 5
BOX_AREA = (0, 140, 1000, 950) # x1, y1, x2, y2

FROM_TIME = "08-30-00"
TO_TIME = "15-00-00"

        
DATA_COLUMNS = ["over", "under", "upper_price", "downer_price",
    "over_player", "over_1_player", "over_2_player", "over_3_player", "over_4_player",
    "over_5_player", "over_6_player", "over_7_player", "over_8_player",
    "over_9_player", "over_10_player", "over_11_player", "over_12_player",
    "over_13_player", "over_14_player", "over_15_player", "over_16_player",

    "over_sell", "over_1_sell", "over_2_sell", "over_3_sell", "over_4_sell",
    "over_5_sell", "over_6_sell", "over_7_sell", "over_8_sell",
    "over_9_sell", "over_10_sell", "over_11_sell", "over_12_sell",
    "over_13_sell", "over_14_sell", "over_15_sell", "over_16_sell",

    "under_buy", "under_1_buy", "under_2_buy", "under_3_buy", "under_4_buy",
    "under_5_buy", "under_6_buy", "under_7_buy", "under_8_buy",
    "under_9_buy", "under_10_buy", "under_11_buy", "under_12_buy",
    "under_13_buy", "under_14_buy", "under_15_buy", "under_16_buy",

    "under_player", "under_1_player", "under_2_player", "under_3_player", "under_4_player",
    "under_5_player", "under_6_player", "under_7_player", "under_8_player",
    "under_9_player", "under_10_player", "under_11_player", "under_12_player",
    "under_13_player", "under_14_player", "under_15_player", "under_16_player",
    
    "volume_sum"
]


def main():
    ocr = predict.OCR("model/model.hdf5")
    data_list = []
    
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    today = datetime.datetime.today()
    hms = today.strftime("%Y-%m-%d")
    video = cv2.VideoWriter('video_{}.mp4'.format(hms), fourcc, FPS, SHAPE)
    before_img = None
    wait()
    for i in range(390*60):
    #for i in range(1*60):
        time.sleep(1)
        print(i)
        img = get_screen_shot()
        img = cv2.resize(img, SHAPE)
        #if before_img is None or not is_same_img(img, before_img):
        time_png = get_time_img()
        png = Image.fromarray(img)
        today = datetime.datetime.today()
        t = today.strftime("%Y-%m-%d-%H-%M-%S")
        #over_value, under_value, upper_price_value, downer_price_value = ocr.predict(png)
        ocr_data = ocr.predict(png)
        print("{}_{}_{}_{}".format(ocr_data["over"], ocr_data["under"], ocr_data["upper_price"], ocr_data["downer_price"]), flush=True)
        data = [t] + [ocr_data[col] for col in DATA_COLUMNS]
        data_list.append(data)
        
        #print("{}_{}_{}_{}".format(over_value, under_value, upper_price_value, downer_price_value), flush=True)
        #data = [t, over_value, under_value, upper_price_value, downer_price_value]
        #data_list.append(data)
        png.paste(time_png, (png.size[0] - time_png.size[0], 0))
        img_pasted = numpy.array(png)
        video.write(img_pasted)
        before_img = img
        if not market_time():
            break
    video.release()
    #df = pandas.DataFrame(data_list, columns=["time", "over", "under", "upper_price", "downer_price"])
    df = pandas.DataFrame(data_list, columns=["time"]+DATA_COLUMNS)
    df.to_csv("log_{}.csv".format(hms), index=False)
    df2 = df.query(
    "over >= 50000 and over <= 2000000"
).query(
    "under >= 50000 and under <= 2000000"
).query(
    "upper_price >= 2500 and upper_price <= 10000"
).assign(
    over_under=lambda df: df["over"] / df["under"],
    hms=lambda df: df["time"].apply(lambda x: x[11:])
).query("'09-00-00' <= hms <= '11-30-00' or '12-30-00' <= hms")

    df2.to_csv("log_processed_{}.csv".format(hms), index=False)
    #os.system("shutdown -s -t 5")

def test2():
    mp4_filepath = "prod_converter_data/video_2020-09-25.mp4"
    ocr = predict.OCR("model/model.hdf5")
    data_list = []

    filename_without_suffix = mp4_filepath.split(".")[0]
    output_dirpath = "output_csv/{}".format(filename_without_suffix)
    
    #os.system("rm -rf {}".format(output_dirpath))
    #os.makedirs(output_dirpath, exist_ok=True)
    
    cap = cv2.VideoCapture(mp4_filepath)
    
    digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))
    before_frame = None
    n = 0
    t = 0
    while True:
        n += 1
        ret, frame = cap.read()
        if ret:
            png = Image.fromarray(frame)
            ocr_data = ocr.predict(png)
            #print(ocr_data)
            print("{}_{}_{}_{}".format(ocr_data["over"], ocr_data["under"], ocr_data["upper_price"], ocr_data["downer_price"]), flush=True)
            data = [n] + [ocr_data[col] for col in DATA_COLUMNS]
            data_list.append(data)
        else:
            break
    #df = pandas.DataFrame(data_list, columns=["time"]+DATA_COLUMNS)
    #df = pandas.DataFrame(data_list, columns=["time", "over", "under", "upper_price", "downer_price"])
    #df.to_csv("output_csv/{}.csv".format(filename_without_suffix), index=False)
    

def wait():
    for i in range(390*60):
        time.sleep(1)
        #print("wait")
        if market_time():
            break

def market_time():
    today = datetime.datetime.today()
    hms = today.strftime("%H-%M-%S")
    return FROM_TIME <= hms <= TO_TIME

def get_time_img():
    time_text_position = (5, 25)
    mask = Image.new("RGB", (150, 50), 0)
    draw = ImageDraw.Draw(mask)
    today = datetime.datetime.today()
    message = today.strftime("%Y-%m-%d-%H-%M-%S")
    draw.text(time_text_position, message, fill=(255, 255, 255))
    mask_2 = mask.resize((300, 100))
    return mask_2

def is_same_img(img, before_img):
    return (img == before_img).all()

def get_screen_shot():
    img = ImageGrab.grab(bbox=BOX_AREA)
    img_array = numpy.array(img)
    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    #png = Image.fromarray(img_array_rgb)
    return img_array

def test():
    ocr = predict.OCR("model/model.hdf5")
    data_list = []
    
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    today = datetime.datetime.today()
    hms = today.strftime("%Y-%m-%d")
    video = cv2.VideoWriter('video_{}.mp4'.format(hms), fourcc, FPS, SHAPE)
    before_img = None
    for i in range(60):
        time.sleep(1)
        print(i)
        img = get_screen_shot()
        img = cv2.resize(img, SHAPE)
        #if before_img is None or not is_same_img(img, before_img):
        time_png = get_time_img()
        png = Image.fromarray(img)
        today = datetime.datetime.today()
        t = today.strftime("%Y-%m-%d-%H-%M-%S")
        #over_value, under_value, upper_price_value, downer_price_value = ocr.predict(png)
        ocr_data = ocr.predict(png)
        print("{}_{}_{}_{}".format(ocr_data["over"], ocr_data["under"], ocr_data["upper_price"], ocr_data["downer_price"]), flush=True)
        data = [t] + [ocr_data[col] for col in DATA_COLUMNS]
        data_list.append(data)
        
        png.paste(time_png, (png.size[0] - time_png.size[0], 0))
        img_pasted = numpy.array(png)
        video.write(img_pasted)
        before_img = img
        if not market_time():
            break
    video.release()
    df = pandas.DataFrame(data_list, columns=["time"]+DATA_COLUMNS)
    df.to_csv("test.csv".format(hms), index=False)

if __name__ == "__main__":
    #main()
    test2()
    #test()