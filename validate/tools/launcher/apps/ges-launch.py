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

import os
import sys
import urlparse
import subprocess
import utils
from urllib import unquote
import xml.etree.ElementTree as ET
from baseclasses import GstValidateTest, TestsManager, ScenarioManager

GES_DURATION_TOLERANCE = utils.GST_SECOND / 2

GES_LAUNCH_COMMAND = "ges-launch-1.0"
if "win32" in sys.platform:
    GES_LAUNCH_COMMAND += ".exe"


GES_ENCODING_TARGET_COMBINATIONS = [
    utils.MediaFormatCombination("ogg", "vorbis", "theora"),
    utils.MediaFormatCombination("webm", "vorbis", "vp8"),
    utils.MediaFormatCombination("mp4", "mp3", "h264"),
    utils.MediaFormatCombination("mkv", "vorbis", "h264")]


def quote_uri(uri):
    """
    Encode a URI/path according to RFC 2396, without touching the file:/// part.
    """
    # Split off the "file:///" part, if present.
    parts = urlparse.urlsplit(uri, allow_fragments=False)
    # Make absolutely sure the string is unquoted before quoting again!
    raw_path = unquote(parts.path)
    return utils.path2url(raw_path)


def find_xges_duration(path):
    root = ET.parse(path)
    for l in root.iter():
        if l.tag == "timeline":
            return long(l.attrib['metadatas'].split("duration=(guint64)")[1].split(" ")[0].split(";")[0])

    return None


class GESTest(GstValidateTest):
    def __init__(self, classname, options, reporter, project_uri, scenario=None,
                 combination=None):
        super(GESTest, self).__init__(GES_LAUNCH_COMMAND, classname, options, reporter,
                                      scenario=scenario)
        self.project_uri = project_uri
        self.duration = find_xges_duration(utils.url2path(project_uri))
        if self.duration is not None:
            self.duration = self.duration / utils.GST_SECOND
        else:
            self.duration = 2 * 60

    def set_sample_paths(self):
        if not self.options.paths:
            if self.options.disable_recurse:
                return
            paths = [os.path.dirname(utils.url2path(self.project_uri))]
        else:
            paths = self.options.paths

        if not isinstance(paths, list):
            paths = [paths]

        for path in paths:
            # We always want paths separator to be cut with '/' for ges-launch
            path = path.replace("\\", "/")
            if not self.options.disable_recurse:
                self.add_arguments("--sample-path-recurse", quote_uri(path))
            else:
                self.add_arguments("--sample-path", quote_uri(path))

    def build_arguments(self):
        GstValidateTest.build_arguments(self)

        if self.options.mute:
            self.add_arguments(" --mute")

        self.set_sample_paths()
        self.add_arguments("-l", self.project_uri)


class GESPlaybackTest(GESTest):
    def __init__(self, classname, options, reporter, project_uri, scenario):
        super(GESPlaybackTest, self).__init__(classname, options, reporter,
                                      project_uri, scenario=scenario)

    def get_current_value(self):
        return self.get_current_position()


class GESRenderTest(GESTest):
    def __init__(self, classname, options, reporter, project_uri, combination):
        super(GESRenderTest, self).__init__(classname, options, reporter,
                                      project_uri)
        self.combination = combination

    def build_arguments(self):
        GESTest.build_arguments(self)
        self._set_rendering_info()

    def _set_rendering_info(self):
        self.dest_file = path = os.path.join(self.options.dest,
                                             self.classname.replace(".render.", os.sep).
                                             replace(".", os.sep))
        utils.mkdir(os.path.dirname(urlparse.urlsplit(self.dest_file).path))
        if not utils.isuri(self.dest_file):
            self.dest_file = utils.path2url(self.dest_file)

        profile = utils.get_profile(self.combination,
                                    video_restriction="video/x-raw,format=I420")
        self.add_arguments("-f", profile, "-o", self.dest_file)

    def check_results(self):
        if self.result is Result.PASSED and self.scenario is None:
            res, msg = utils.compare_rendered_with_original(self.duration, self.dest_file)
            self.set_result(res, msg)
        else:
            if self.result == utils.Result.TIMEOUT:
                missing_eos = False
                try:
                    if utils.get_duration(self.dest_file) == self.duration:
                        missing_eos = True
                except Exception as e:
                    pass

                if missing_eos is True:
                    self.set_result(utils.Result.TIMEOUT, "The rendered file add right duration, MISSING EOS?\n",
                                    "failure", e)
            else:
                GstValidateTest.check_results(self)

    def get_current_value(self):
        return self.get_current_size()


class GESTestsManager(TestsManager):
    name = "ges"

    _scenarios = ScenarioManager()

    def __init__(self):
        super(GESTestsManager, self).__init__()

    def init(self):
        try:
            if "--set-scenario=" in subprocess.check_output([GES_LAUNCH_COMMAND, "--help"]):

                return True
            else:
                self.warning("Can not use ges-launch, it seems not to be compiled against"
                             " gst-validate")
        except subprocess.CalledProcessError as e:
            self.warning("Can not use ges-launch: %s" % e)
        except OSError as e:
            self.warning("Can not use ges-launch: %s" % e)

    def add_options(self, parser):
        group = parser.add_argument_group("GStreamer Editing Services specific option"
                            " and behaviours",
                            description="""
The GStreamer Editing Services launcher will be usable only if GES has been compiled against GstValidate
You can simply run scenarios specifying project as args. For example the following will run all available
and activated scenarios on project.xges:

    $gst-validate-launcher ges /some/ges/project.xges


Available options:""")
        group.add_argument("-P", "--projects-paths", dest="projects_paths",
                         default=os.path.join(utils.DEFAULT_GST_QA_ASSETS,
                                              "ges-projects"),
                         help="Paths in which to look for moved medias")
        group.add_argument("-r", "--disable-recurse-paths", dest="disable_recurse",
                         default=False, action="store_true",
                         help="Whether to recurse into paths to find medias")

    def set_settings(self, options, args, reporter):
        TestsManager.set_settings(self, options, args, reporter)

        try:
            os.makedirs(utils.url2path(options.dest)[0])
        except OSError:
            pass

    def list_tests(self):
        if self.tests:
            return self.tests

        projects = list()
        if not self.args:
            path = self.options.projects_paths
            for root, dirs, files in os.walk(path):
                for f in files:
                    if not f.endswith(".xges"):
                        continue
                    projects.append(utils.path2url(os.path.join(path, root, f)))
        else:
            for proj in self.args:
                if not utils.isuri(proj):
                    proj = utils.path2url(proj)

                if os.path.exists(proj):
                    projects.append(proj)

        SCENARIOS = ["play_15s",
                     "seek_forward",
                     "seek_backward",
                     "scrub_forward_seeking"]
        for proj in projects:
            # First playback casses
            for scenario_name in SCENARIOS:
                scenario = self._scenarios.get_scenario(scenario_name)
                if scenario is None:
                    continue
                classname = "ges.playback.%s.%s" % (scenario.name,
                                                    os.path.basename(proj).replace(".xges", ""))
                self.add_test(GESPlaybackTest(classname,
                                              self.options,
                                              self.reporter,
                                              proj,
                                              scenario=scenario)
                                  )

            # And now rendering casses
            for comb in GES_ENCODING_TARGET_COMBINATIONS:
                classname = "ges.render.%s.%s" % (str(comb).replace(' ', '_'),
                                                  os.path.splitext(os.path.basename(proj))[0])
                self.add_test(GESRenderTest(classname, self.options,
                                            self.reporter, proj,
                                            combination=comb)
                                  )

        return self.tests
