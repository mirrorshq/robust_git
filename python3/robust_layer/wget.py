#!/usr/bin/env python3

# wget.py - robust wget operations
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


import re
import sys
from . import TIMEOUT, RETRY_WAIT
from ._util import Util


SOURCE_CONTINUABLE = 1
SOURCE_NOT_CONTINUABLE = 2
SOURCE_DETECT_CONTINUABLE = 3


def additional_param(source_continuable=SOURCE_CONTINUABLE):
    if source_continuable == SOURCE_CONTINUABLE:
        return ["-t", "0", "-w", str(RETRY_WAIT), "--random-wait", "-T", str(TIMEOUT)]
    elif source_continuable == SOURCE_NOT_CONTINUABLE:
        # we don't modify "--read-timeout" here so that the connection is kept as long as possible
        return ["-t", "0", "-w", str(RETRY_WAIT), "--random-wait", "--dns-timeout=%d" % (TIMEOUT), "--connect-timeout=%d" % (TIMEOUT)]
    else:
        assert False


def exec(*args, source_continuable=SOURCE_CONTINUABLE):
    # FIXME: SOURCE_DETECT_CONTINUABLE is not supported yet
    # and wget sucks that it does not detect continuable so user can specify different timeout natively!
    # there would be zero performance impact if wget do this natively
    # and there would be no need for "source_continuable" parameter
    assert source_continuable in [SOURCE_CONTINUABLE, SOURCE_NOT_CONTINUABLE]

    for x in args:
        assert x != "--random-wait"
        assert not re.fullmatch("(-t|--tries|-w|--wait|-T|--timetout|--dns-timeout|--connect-timeout|--read-timeout)(=.*)?", x)
    args = list(args)

    # Util.cmdListExec() use pipe to do advanced process, here is to ensure progress is not affected
    if sys.stderr.isatty():
        bFound = False
        for i in range(0, len(args)):
            if args[i].startswith("--progress=") and not args[i].endswith(":force"):
                args[i] += ":force"
                bFound = True
        if not bFound:
            args.insert(0, "--progress=bar:force")

    Util.cmdListExec(["/usr/bin/wget"] + additional_param(source_continuable) + args)


class PrivateUrlNotExistError(Exception):
    pass
