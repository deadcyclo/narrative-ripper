#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Brendan Johan Lee <deadcyclo@vanntett.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import multiprocessing, json, os, string, urllib, sys

try:
    from colorama import init, Fore, Back, Style
    colors = True
except ImportError:
    colors = False

hd_paths = ['images/hd/', 'videos/1080p/', 'videos/720p', 'videos/480p']
sd_paths = ['images/webrender', 'images/smartphone', 'images/thumbnails', 'images/covers', 'images/keyframes', 'images/videocovers']
    
def mkdir_recursive(path):
    sub_path = os.path.dirname(path)
    if not os.path.exists(sub_path):
        mkdir_recursive(sub_path)
    if not os.path.exists(path):
        os.mkdir(path)
    
def safe_print(content):
    #Avoid raise conditions on print
    print "{0}\n".format(content),
    
def cgreen(string):
    if colors:
        safe_print(Fore.BLACK + Back.GREEN +Style.BRIGHT + string)
    else:
        safe_print(string)

def cred(string):
    if colors:
        safe_print(Fore.RED + Back.RESET + Style.BRIGHT + string)
    else:
        safe_print(string)
        
def cyellow(string):
    if colors:
        safe_print(Fore.BLACK + Back.YELLOW + Style.BRIGHT + string)
    else:
        safe_print(string)

def cblue(string):
    if colors:
        safe_print(Fore.BLUE + Back.RESET + Style.BRIGHT + string)
    else:
        safe_print(string)
        
def creset():
    if colors:
        print(Style.RESET_ALL)

def get_photo_urls(path, type, storage_subpath):
    photos = []
    for f in os.listdir(os.path.join(path, 'metadata/moments')):
        fname = os.path.join(path, 'metadata/moments', f)
        if (os.path.isdir(fname)):
            for jsonn in os.listdir(fname):
                jsonf = os.path.join(fname, jsonn)
                if (os.path.isfile(jsonf)) and jsonn.startswith('photos'):
                    with open(jsonf) as data_file:
                        data = json.load(data_file)
                        for image in data['results']:
                            photos.append({'url' : image['renders'][type]['url'], 'dir' : os.path.join(path, storage_subpath.format(uuid=image['moment_uuid']))})
    return photos

def get_cover_photo_urls(path, storage_subpath):
    photos = []
    for f in os.listdir(os.path.join(path, 'metadata/moments')):
        fname = os.path.join(path, 'metadata/moments', f)
        if (os.path.isdir(fname)):
            for jsonn in os.listdir(fname):
                jsonf = os.path.join(fname, jsonn)
                if (os.path.isfile(jsonf)) and jsonn.startswith('moment'):
                    with open(jsonf) as data_file:
                        data = json.load(data_file)
                        for cover_photo in data['cover_photos']:
                            for img in cover_photo['renders']:
                                photos.append({'url' : cover_photo['renders'][img]['url'], 'dir' : os.path.join(path, storage_subpath.format(uuid=data['uuid'], type=img))})                        
    return photos

def get_keyframe_urls(path, storage_subpath):
    photos = []
    for f in os.listdir(os.path.join(path, 'metadata/moments')):
        fname = os.path.join(path, 'metadata/moments', f)
        if (os.path.isdir(fname)):
            for jsonn in os.listdir(fname):
                jsonf = os.path.join(fname, jsonn)
                if (os.path.isfile(jsonf)) and jsonn.startswith('moment'):
                    with open(jsonf) as data_file:
                        data = json.load(data_file)
                        for render in data['keyframe']['renders']:
                            photos.append({'url' : data['keyframe']['renders'][render]['url'], 'dir' : os.path.join(path, storage_subpath.format(uuid=data['uuid'], type=render))})
    return photos    
                            
def get_video_urls(path, type, storage_subpath):
    videos = []
    for f in os.listdir(os.path.join(path, 'metadata/timeline')):
        fname = os.path.join(path, 'metadata/timeline', f)
        if (os.path.isfile(fname)):
            with open(fname) as data_file:
                data = json.load(data_file)
                for tl in data['results']:
                    if tl['type'] == 'video':                        
                        if type in tl['renders']:
                            videos.append({'url' : tl['renders'][type]['url'], 'dir' : os.path.join(path, storage_subpath.format(uuid=tl['uuid']))})
    return videos

def get_video_cover_urls(path, storage_subpath):
    photos = []
    for f in os.listdir(os.path.join(path, 'metadata/timeline')):
        fname = os.path.join(path, 'metadata/timeline', f)
        if (os.path.isfile(fname)):
            with open(fname) as data_file:
                data = json.load(data_file)
                for tl in data['results']:
                    if tl['type'] == 'video':
                        cnt = 1
                        for thumb in tl['video_thumbs']:
                            for render in thumb['renders']:
                                photos.append({'url' : thumb['renders'][render]['url'], 'dir' : os.path.join(path, storage_subpath.format(uuid=tl['uuid'], type=render, cnt=cnt))})
                            cnt += 1                        
    return photos

def get_photos_by_type(pool, path, type, storagepath, message, foundmessage):
    cgreen(message)
    files = get_photo_urls(path, type, storagepath)
    cyellow(foundmessage.format(cnt=len(files)))
    pool.map(download_file, files)

def get_cover_photos(pool, path, storagepath, message, foundmessage):
    cgreen(message)
    files = get_cover_photo_urls(path, storagepath)
    cyellow(foundmessage.format(cnt=len(files)))
    pool.map(download_file, files)

def get_keyframe_photos(pool, path, storagepath, message, foundmessage):
    cgreen(message)
    files = get_keyframe_urls(path, storagepath)
    cyellow(foundmessage.format(cnt=len(files)))
    pool.map(download_file, files)    

def get_videos_by_type(pool, path, type, storagepath, message, foundmessage):
    cgreen(message)
    files = get_video_urls(path, type, storagepath)
    cyellow(foundmessage.format(cnt=len(files)))
    pool.map(download_file, files)

def get_video_covers(pool, path, storagepath, message, foundmessage):
    cgreen(message)
    files = get_video_cover_urls(path, storagepath)
    cyellow(foundmessage.format(cnt=len(files)))
    pool.map(download_file, files)    
    
def download_file(file):
    if not os.path.exists(file['dir']):
        mkdir_recursive(file['dir'])
    filename = string.split(file['url'], '/')[-1]
    filefullname = os.path.join(file['dir'], filename)
    if os.path.isfile(filefullname):
        cred('[{proc}] -> skipping {file} as it exists'.format(proc=os.getpid(), file=filename))
    else:
        cblue('[{proc}] -> {url}'.format(proc=os.getpid(), url=file['url']))
        image=urllib.URLopener()
        image.retrieve(file['url'], filefullname)

def create_paths(path, paths):
    for p in paths:
        if not os.path.exists(os.path.join(path, p)):
            mkdir_recursive(os.path.join(path, p))

if __name__ == "__main__":
    path = raw_input("Where to download to (metadata subfolder must be in place)? ")
    processes = raw_input("How many threads should I use? (hint: if uncertain use the number of cores your processor has) ")
    all = False
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        all = True

    # Need to create paths here to avoid raise conditions in the threads
    create_paths(path, hd_paths)

    pool=multiprocessing.Pool(processes=int(processes))
    get_photos_by_type(pool, path, 'g1_hd', 'images/hd/{uuid}', ' Finding HD photos ', ' Downloading {cnt} HD photos')
    get_videos_by_type(pool, path, 'g1_1080p', 'videos/1080p/{uuid}', ' Finding 1080p photos ', ' Downloading {cnt} 1080p videos')
    get_videos_by_type(pool, path, 'g1_720p', 'videos/720p/{uuid}', ' Finding 720p photos ', ' Downloading {cnt} 720p videos')
    get_videos_by_type(pool, path, 'g1_480p', 'videos/480p/{uuid}', ' Finding 480p photos ', ' Downloading {cnt} 480p videos')        
    
    if all:
        create_paths(path, sd_paths)
        get_photos_by_type(pool, path, 'g1_webrender', 'images/webrender/{uuid}', ' Finding webrender photos ', ' Downloading {cnt} webrender photos')
        get_photos_by_type(pool, path, 'g1_thumb_square', 'images/thumbnails/{uuid}', ' Finding thumbnail photos ', ' Downloading {cnt} thumbnail photos')
        get_photos_by_type(pool, path, 'g1_smartphone', 'images/smartphone/{uuid}', ' Finding smartphone photos ', ' Downloading {cnt} smartphone photos')
        get_cover_photos(pool, path, 'images/covers/{uuid}/{type}', ' Finding cover images ', ' Downloading {cnt} cover images')
        get_keyframe_photos(pool, path, 'images/keyframes/{uuid}/{type}', ' Finding keyframe images ', ' Downloading {cnt} keyframe images')
        get_video_covers(pool, path, 'images/videocovers/{uuid}/{cnt}/{type}', ' Finding video cover images ', ' Downloading {cnt} video cover images')
    
    cgreen(' DONE ')
    creset()
