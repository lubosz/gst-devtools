#!/usr/bin/env python2
#
# Copyright (c) 2013,Thibault Saunier <thibault.saunier@collabora.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA 02110-1301, USA.
""" Some utilies. """

import sys
import os
import re
import urllib
import loggable
import urlparse
import subprocess

from operator import itemgetter


GST_SECOND = long(1000000000)
DEFAULT_TIMEOUT = 30
DEFAULT_MAIN_DIR = os.path.expanduser("~/gst-validate/")
DEFAULT_GST_QA_ASSETS =  os.path.join(DEFAULT_MAIN_DIR, "gst-qa-assets")
DISCOVERER_COMMAND = "gst-discoverer-1.0"
DURATION_TOLERANCE = GST_SECOND / 2
# Use to set the duration from which a test is concidered as being 'long'
LONG_TEST = 40

class Result(object):
    NOT_RUN = "Not run"
    FAILED = "Failed"
    TIMEOUT = "Timeout"
    PASSED = "Passed"
    KNOWN_ERROR = "Known error"


class Protocols(object):
    HTTP = "http"
    FILE = "file"
    HLS = "hls"


class Colors(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def desactivate_colors():
    Colors.HEADER = ''
    Colors.OKBLUE = ''
    Colors.OKGREEN = ''
    Colors.WARNING = ''
    Colors.FAIL = ''
    Colors.ENDC = ''


def mkdir(directory):
    try:
        os.makedirs(directory)
    except os.error:
        pass


def which(name):
    result = []
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    path = os.environ.get('PATH', None)
    if path is None:
        return []
    for p in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, os.X_OK):
            result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, os.X_OK):
                result.append(pext)
    return result


def get_color_for_result(result):
    if result is Result.FAILED:
        color = Colors.FAIL
    elif result is Result.TIMEOUT:
        color = Colors.WARNING
    elif result is Result.PASSED:
        color = Colors.OKGREEN
    else:
        color = Colors.OKBLUE

    return color


def printc(message, color="", title=False):
    if title:
        length = 0
        for l in message.split("\n"):
            if len(l) > length:
                length = len(l)
        if length == 0:
            length = len(message)
        message = length * '=' + "\n" + str(message) + "\n" + length * '='

    if hasattr(message, "result") and color == '':
        color = get_color_for_result(message.result)

    sys.stdout.write(color + str(message) + Colors.ENDC + "\n")
    sys.stdout.flush()


def launch_command(command, color=None, fails=False):
    printc(command, Colors.OKGREEN, True)
    res = os.system(command)
    if res != 0 and fails is True:
        raise subprocess.CalledProcessError(res, "%s failed" % command)


def path2url(path):
    return urlparse.urljoin('file:', urllib.pathname2url(path))


def url2path(url):
    path = urlparse.urlparse(url).path
    if "win32" in sys.platform:
        if path[0] == '/':
            return path[1:] # We need to remove the first '/' on windows
    return path


def isuri(string):
    url = urlparse.urlparse(string)
    if url.scheme != "" and  url.scheme != "":
        return True

    return False

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def get_subclasses(klass, env):
    subclasses = []
    for symb in env.iteritems():
        try:
            if issubclass(symb[1], klass) and not symb[1] is klass:
                subclasses.append(symb[1])
        except TypeError:
            pass

    return subclasses

##############################
#    Encoding related utils  #
##############################
class MediaFormatCombination(object):

    def __str__(self):
        return "%s and %s in %s" % (self.acodec, self.vcodec, self.container)

    def __init__(self, container, acodec, vcodec):
        self.container = container
        self.acodec = acodec
        self.vcodec = vcodec


FORMATS = {"aac": "audio/mpeg,mpegversion=4",
           "ac3": "audio/x-ac3",
           "vorbis": "audio/x-vorbis",
           "mp3": "audio/mpeg,mpegversion=1,layer=3",
           "h264": "video/x-h264",
           "vp8": "video/x-vp8",
           "theora": "video/x-theora",
           "ogg": "application/ogg",
           "mkv": "video/x-matroska",
           "mp4": "video/quicktime,variant=iso;",
           "webm": "video/webm"}


def get_profile_full(muxer, venc, aenc, video_restriction=None,
                     audio_restriction=None,
                     audio_presence=0, video_presence=0):
    ret = "\""
    if muxer:
        ret += muxer
    ret += ":"
    if venc:
        if video_restriction is not None:
            ret = ret + video_restriction + '->'
        ret += venc
        if video_presence:
            ret = ret + '|' + str(video_presence)
    if aenc:
        ret += ":"
        if audio_restriction is not None:
            ret = ret + audio_restriction + '->'
        ret += aenc
        if audio_presence:
            ret = ret + '|' + str(audio_presence)

    ret += "\""
    return ret.replace("::", ":")


def get_profile(combination, video_restriction=None, audio_restriction=None):
    return get_profile_full(FORMATS[combination.container],
                            FORMATS[combination.vcodec],
                            FORMATS[combination.acodec],
                            video_restriction=video_restriction,
                            audio_restriction=audio_restriction)

##################################################
#  Some utilities to parse gst-validate output   #
##################################################
def gsttime_from_tuple(stime):
    return long((int(stime[0]) * 3600 + int(stime[1]) * 60 + int(stime[2])) * GST_SECOND +  int(stime[3]))

timeregex = re.compile(r'(?P<_0>.+):(?P<_1>.+):(?P<_2>.+)\.(?P<_3>.+)')
def parse_gsttimeargs(time):
    stime = map(itemgetter(1), sorted(timeregex.match(time).groupdict().items()))
    return long((int(stime[0]) * 3600 + int(stime[1]) * 60 + int(stime[2])) * GST_SECOND +  int(stime[3]))

def get_duration(media_file):

    duration = 0
    try:
        res = subprocess.check_output([DISCOVERER_COMMAND, media_file])
    except subprocess.CalledProcessError:
        # gst-media-check returns !0 if seeking is not possible, we do not care in that case.
        pass

    for l in res.split('\n'):
        if "Duration: " in l:
            duration = parse_gsttimeargs(l.replace("Duration: ", ""))
            break

    return duration


def compare_rendered_with_original(orig_duration, dest_file, tolerance=DURATION_TOLERANCE):
        duration = get_duration(dest_file)

        if orig_duration - tolerance >= duration >= orig_duration + tolerance:
            return (Result.FAILED, "Duration of encoded file is "
                    " wrong (%s instead of %s)" %
                    (orig_duration / GST_SECOND,
                    duration / GST_SECOND),
                    "wrong-duration")
        else:
            return (Result.PASSED, "")


def get_scenarios():
    GST_VALIDATE_COMMAND = "gst-validate-1.0"
    os.system("%s --scenarios-defs-output-file %s" % (GST_VALIDATE_COMMAND,
                                                      ))
