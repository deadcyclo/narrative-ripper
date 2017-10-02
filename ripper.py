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

import requests, time, json, string, os.path, sys, argparse, getpass

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
    retries = 0
    while 'r' not in locals() or r.status_code != 200:
        r = session.get(url)
        if r.status_code != 200:
            if max_retry > 0 and retries == max_retry:
                return None
            print "Failed {url}. Retrying in 1 second.".format(url=url)
            time.sleep(1)
            retries += 1
    return r.json()

def get_from_file_or_service(session, url, subpath, name):
    if file_exists(subpath, name):
        print "Retrieving {url} from file".format(url=url)
        with open(os.path.join(path, subpath, name)) as data_file:    
            return json.load(data_file)
    data = get_url(session, url)
    if data is not None:
        print_to_file(subpath, name, data)
    time.sleep(1)
    return data

def get_multiple(session, url, subpath, name):
    data = get_from_file_or_service(session, url, subpath, name.format(cnt=1))
    if data is None:
        return None
    cnt = 2
    while data['next'] is not None:
        data = get_from_file_or_service(session, data['next'], subpath, name.format(cnt=cnt))
        cnt += 1
    
def get_moments(session, url, subpath, name):
    moments = None
    while moments == None:
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

def get_token(email, password):
    params = { "grant_type": "password", "client_id": "ios", "email": email, "password": password }
    return json.loads(requests.post("https://narrativeapp.com/oauth2/token/", params).text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Narrative Ripper')
    parser.add_argument('-m', '--max-retry', help='max retry; when it is not specified or its value is zero or negative, ripper will retry indefinitely', required=False)
    parser.add_argument('-e', '--email', help='account email', required=False)
    parser.add_argument('-p', '--password', help='account password', required=False)
    parser.add_argument('-o', '--output_path', help='output path', required=False)
    args = vars(parser.parse_args())

    global max_retry
    if args['max_retry'] is None:
        max_retry = 0
    else:
        max_retry = int(args['max_retry'])        

    if args['email'] is None:
        email = raw_input("Enter your email address: ")
    else:
        email = args['email']

    if args['password'] is None:
        password = getpass.getpass(prompt='Enter your password: ')
    else:
        password = args['password']

    try:
        token = get_token(email, password)
    except:
        print "Incorrect email or password."
        sys.exit(-1)

    global path
    if args['output_path'] is None:
        path = raw_input("Where do you want to store stuff? ")
    else:
        path = args['output_path']

    do_token_stuff(token)
