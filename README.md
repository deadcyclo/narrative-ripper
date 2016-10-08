# Narrative Ripper

Narrative ripper is a download utility used to download your data,
images and videos from the Narrative Clip Cloud. I wrote this tool
because Narrative is closing down, and the download application they
are currently working on is slow, unstable, doesn't work properly and
isn't available for Linux and I wanted to be sure I got as much as
possible of my data before their servers shut down.

The ripper is two separate applications, one for downloading the
metadata and one for downloading images and videos. The applications
can be re-run and will continue from where they left of, so they are
safe to use even if they stall out or you quit the application before
it has finished running. However, the applications are single use, so
if you upload anything to the cloud after running the application,
re-running the application will not grab the new content. (But why
would you continue uploading stuff now?).

The download application that downloads images and videos is
multithreaded and you decide how many threads you want to run (tip:
Use the same amount of threads as you have processor cores for the
fastest possible download).

NOTE: The Narrative API is very unstable at the moment, therefore the
metadatadownloader will continue retrying each request until it
succeeds, so you will not miss anything. Due to the unstability (which
probably is due to a lot of people trying to grab their data), I've
decided to enforece a one second cool off between each API call to
lighten the load on their server. Please respect this. Don't
worry. The 1 second delay only applies to downloading metadata from
the API. Once that is done and you start downloading images and videos
you will get full speed with no delays.

The application is written in python and tested on Ubuntu, but should
run on any operating system that python runs on. No additional python
packages are required (if you discover that a package is missing from
your python distribution resulting in errors running the application
please open a ticket and let me know). However, if you install the
colorama package you get nice colorized output in the downloader, but
this isn't required.

The application was written and tested in a single afternoon, so there
is some copy paste code that could potentially be gotten rid of (feel
free to send me a pull request).

## A note on metadata

Since I wanted to be sure to get all of my data as soon as possible
before the servers shut down, all metadata is stored separately and
nothing is added to the photos exif data. **HOWEVER, I want my images
to have exif data. I will be releasing tools here to add exif data to
the downloaded photos from the downloaded metadata here shortly. Stay
tuned!**

## What is downloaded

* Most metadata (inkluding GPS location data - not added to exif, yet...)
* HD quality photos
* All video formats
* (Optional) All other photo qualities
* (Optional) All cover photos
* (Optional) Video cover photos
* (Optional) Video key frames

## What isn't downloaded (yet)

* account and device info
* tags
* comments
* faces

The reason these aren't included yet is because a) I haven't used the
features, and b) I wanted to get this tool out there as soon as
possible. I will be adding all of these features shortly. ** Don't
wait for these features. Once they are included you can rerun the tool
and this additional data will be downloaded without having to
redownload everything. Be safe. Grab your data as soon as possible! **

## Usage

### Register an application

* Go to <http://open.getnarrative.com/apps> and register an application
* Use <http://localhost:4576> as the redirect URI when prompted
* Make a note of your api client id and api client secret

### Run the metadata downloader

First we are going to download all of your metadata from Narrative. We
do this separately with a separate command since the Narrative API is
slow and unstable, and we want the photo and video downloads to go as
fast as possible.

* run the command `python ripper.py`
* when prompted enter your api client id
* when prompted enter your api client secret
* when prompted enter the full path to where you would like to download your data from Narrative to
* sit back and wait

### Run the content downloader

Once all of your metadata is stored, it's time to download the actual
content. But first. Decide if you want to download all content, or
only HD quality images and all videos. (If you decide to only download
HD quality images and all videos, you can download the other content
later by re-running the application with the all switch and entering
the same full path. The application never redownloads any content, so
you won't have to redownload all of the high quality content).

If you opt to download all content you will in addition to the HD
quality images and all videos also get all of the stored images
formats (including thumbnails), the cover photos for all of your
moments, and the cover photos and keyframes for all of your videos.

* If you only want HD images and all videos run the command `python downloader.py`
* If you want all content run the command `python downloader.py all`
* when prompted enter the **exact same full path** you entered when running the ripper
* sit back and wait

## Bug reporting

Please open a ticket here on github, and I'll get back to you as soon
as possible. I'm happy to answer emails, but that might be a slower
route than simply opening a ticket.

## Contributing

I would be very happy for any contributions. Fork the project and send
me a pull request.

## License

Copyright 2016 Brendan Johan Lee <deadcyclo@vanntett.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
