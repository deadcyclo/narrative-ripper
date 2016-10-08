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

# TODO: Download tags, faces, comments, account and device info

from python_oauth2_token import get_token
import requests, time, json, string, os.path

def mkdir_recursive(path):
    sub_path = os.path.dirname(path)
    if not os.path.exists(sub_path):
        mkdir_recursive(sub_path)
    if not os.path.exists(path):
        os.mkdir(path)

def print_to_file(subpath, name, data):
    filename = os.path.join(path, subpath, name)
    ensure_dir(filename)
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def ensure_dir(filename):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        mkdir_recursive(dirname)
        
def file_exists(subpath, name):
    return os.path.isfile(os.path.join(path, subpath, name))

def get_url(session, url):
    print "Retrieving {url} from web".format(url=url)
    while 'r' not in locals() or r.status_code != 200:
        r = session.get(url)
        if r.status_code != 200:
            print "Failed {url}. Retrying in 1 second.".format(url=url)
            time.sleep(1)
    return r.json()

def get_from_file_or_service(session, url, subpath, name):
    if file_exists(subpath, name):
        print "Retrieving {url} from file".format(url=url)
        with open(os.path.join(path, subpath, name)) as data_file:    
            return json.load(data_file)
    data = get_url(session, url)
    print_to_file(subpath, name, data)
    time.sleep(1)
    return data

def get_multiple(session, url, subpath, name):
    data = get_from_file_or_service(session, url, subpath, name.format(cnt=1))
    cnt = 2
    while data['next'] is not None:
        data = get_from_file_or_service(session, data['next'], subpath, name.format(cnt=cnt))
        cnt += 1
    
def get_moments(session, url, subpath, name):
    moments = get_from_file_or_service(session, url, subpath, name)
    for moment in moments['results']:
        moment_path = "metadata/moments/{uuid}".format(uuid=moment['uuid'])
        moment_data = get_from_file_or_service(session, moment['url'], moment_path, "moment.json")        
        get_multiple(session, "https://narrativeapp.com/api/v2/moments/{uuid}/positions/?limit=1500".format(uuid=moment['uuid']), moment_path, "positions-{cnt}.json")
        get_multiple(session, "https://narrativeapp.com/api/v2/moments/{uuid}/photos/?limit=1500".format(uuid=moment['uuid']), moment_path, "photos-{cnt}.json")
    return moments

def do_token_stuff(token):
  print token['access_token']
  session = requests.Session()
  session.headers.update({'Authorization': 'Bearer {key}'.format(key=token['access_token'])})

  moment = get_moments(session, "https://narrativeapp.com/api/v2/moments/?limit=1500", "metadata/moment-overview", "page-1.json")
  cnt = 2
  while moment['next'] is not None:
      moment = get_moments(session, moment['next'], "metadata/moment-overview", "page-{cnt}.json".format(cnt=cnt))
      cnt += 1

  get_multiple(session, "https://narrativeapp.com/api/v2/timeline/?limit=3000", "metadata/timeline", "page-{cnt}.json")

if __name__ == "__main__":
    global path
    apikey = raw_input("Enter your API client id: ")
    apisecret = raw_input("Enter your API client secret: ")
    path = raw_input("Where do you want to store stuff? ")
    get_token(apikey, apisecret, do_token_stuff)

