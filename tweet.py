#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from requests_oauthlib import OAuth1Session
import json
import sys
import urllib.error
import urllib.request
import os
from PIL import Image
import glob

def get_all_tweet(screen_name):
    CK = config.CONSUMER_KEY
    CS = config.CONSUMER_SECRET
    AT = config.ACCESS_TOKEN
    ATS = config.ACCESS_TOKEN_SECRET

    # OAuth認証
    twitter = OAuth1Session(CK, CS, AT, ATS)
    #timelineのURL
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    #対象者のTwitterID
    max_id = None
    timeCounter = [0 for i in range(24)]
    morning = []
    evening = []
    for i in range(2):
        #パラメータ指定
        params = {"count" : 200 ,"screen_name": screen_name,"max_id":max_id, "include_entities":True}
        req = twitter.get(url, params = params)
        # レスポンスを確認
        if req.status_code == 200:
            tweets = json.loads(req.text)
            max_id = tweets[-1]["id"]-1
            for tweet in tweets:
                try:
                    media = tweet["entities"]["media"][0]["media_url"] + ":small"
                    dst_path = 'data/{}/{}'.format(screen_name,media[-18:-6])
                    download_file(media, dst_path)
                    print(media)
                except:
                    continue
        else:
            print ("Error: %d" % req.status_code)
def download_file(url, dst_path):
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(dst_path, mode='wb') as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        print(e)
        
def crop_image(infile, width=None, height=None):
    img = Image.open(infile)

    width_orig, height_orig = img.size
    if not width:
        width = width_orig
    if not height:
        height = height_orig

    center_h = width_orig / 2
    center_v = height_orig / 2
    width_half = width / 2
    height_half = height / 2

    # 中心の切り出し場所の座標を計算する
    left = center_h - width_half
    top = center_v - height_half
    right = center_h + width_half
    bottom = center_v + height_half
    area = (left, top, right, bottom)

    cropped_img = img.crop(area)
    cropped_img.save(infile)
    
    
if __name__ == '__main__':
    args = sys.argv
    screen_name = args[0]
    new_dir_path = 'data/'+screen_name
    os.mkdir(new_dir_path)
    get_all_tweet(screen_name)
    files = glob.glob('./data/{}/*.jpg'.format(screen_name))
    list(map(lambda file: crop_image(file,340,340),files))
    images = list(map(lambda file: Image.open(file), files))
    images[0].save(screen_name+'.gif', save_all=True, append_images=images[1:], duration=0.1, loop=0)
