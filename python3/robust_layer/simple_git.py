#!/usr/bin/env python3

# simple_git.py - robust simple git operations
#
# Copyright (c) 2019-2020 Fpemud <fpemud@sina.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import os
import time
import subprocess
from _util import Util


def clean(dest_dir):
    Util.cmdCall("/usr/bin/git", "-C", dest_dir, "reset", "--hard")  # revert any modifications
    Util.cmdCall("/usr/bin/git", "-C", dest_dir, "clean", "-xfd")    # delete untracked files


def clone(dest_directory, url, quiet=False):
    if quiet:
        quietArg = "-q"
    else:
        quietArg = ""

    while True:
        try:
            cmd = "/usr/bin/git clone %s \"%s\" \"%s\"" % (quietArg, url, dest_directory)
            Util.shellExecWithStuckCheck(cmd, git.additional_environ(), quiet)
            break
        except Util.ProcessStuckError:
            time.sleep(Util.RETRY_TIMEOUT)
        except subprocess.CalledProcessError as e:
            if e.returncode > 128:
                # terminated by signal, no retry needed
                raise
            time.sleep(Util.RETRY_TIMEOUT)


def pull(dest_directory, quiet=False):
    if quiet:
        quietArg = "-q"
    else:
        quietArg = ""

    while True:
        try:
            cmd = "/usr/bin/git -C \"%s\" pull --rebase --no-stat %s" % (dest_directory, quietArg)
            Util.shellExecWithStuckCheck(cmd, git.additional_environ(), quiet)
            break
        except Util.ProcessStuckError:
            time.sleep(Util.RETRY_TIMEOUT)
        except subprocess.CalledProcessError as e:
            if e.returncode > 128:
                # terminated by signal, no retry needed
                raise
            time.sleep(Util.RETRY_TIMEOUT)


def pull_or_reclone(dest_directory, url, quiet=False):
    if quiet:
        quietArg = "-q"
    else:
        quietArg = ""

    mode = "pull"
    if not os.path.exists(dest_directory):
        mode = "clone"
    if mode == "pull" and not os.path.isdir(os.path.join(dest_directory, ".git")):
        mode = "clone"
    if mode == "pull" and url != _gitGetUrl(dest_directory):
        mode = "clone"

    while True:
        if mode == "pull":
            clean(dest_directory)
            try:
                cmd = "/usr/bin/git -C \"%s\" pull --rebase --no-stat %s" % (dest_directory, quietArg)
                Util.shellExecWithStuckCheck(cmd, git.additional_environ(), quiet)
                break
            except Util.ProcessStuckError:
                time.sleep(1.0)
            except subprocess.CalledProcessError as e:
                if e.returncode > 128:
                    raise                    # terminated by signal, no retry needed
                if "fatal: refusing to merge unrelated histories" in str(e.stderr):
                    mode = "clone"
                else:
                    time.sleep(1.0)
        elif mode == "clone":
            Util.forceDelete(dest_directory)
            try:
                cmd = "/usr/bin/git clone %s \"%s\" \"%s\"" % (quietArg, url, dest_directory)
                Util.shellExecWithStuckCheck(cmd, git.additional_environ(), quiet)
                break
            except subprocess.CalledProcessError as e:
                if e.returncode > 128:
                    raise                    # terminated by signal, no retry needed
                time.sleep(1.0)
        else:
            assert False


def _gitGetUrl(dirName):
    gitDir = os.path.join(dirName, ".git")
    cmdStr = "/usr/bin/git --git-dir=\"%s\" --work-tree=\"%s\" config --get remote.origin.url" % (gitDir, dirName)
    return Util.shellCall(cmdStr)
