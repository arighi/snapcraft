# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2015 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import tempfile
import unittest
from unittest.mock import (
    Mock,
    patch,
)

from snapcraft.plugin import Plugin
from snapcraft.plugins.copy import CopyPlugin


class TestPlugin(unittest.TestCase):

    def test_isDirty(self):
        p = Plugin("mock", "mock-part", {}, loadConfig=False)
        p.statefile = tempfile.NamedTemporaryFile().name
        self.addCleanup(os.remove, p.statefile)
        p.code = Mock()
        # pull once
        p.pull()
        p.code.pull.assert_called()
        # pull again, not dirty no need to pull
        p.code.pull.reset_mock()
        p.pull()
        self.assertFalse(p.code.pull.called)

    def test_collectSnapFiles(self):
        p = Plugin("mock", "mock-part", {}, loadConfig=False)

        tmpdirObject = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdirObject.cleanup)
        tmpdir = tmpdirObject.name

        p.installdir = tmpdir + '/install'
        os.makedirs(tmpdir + '/install/1/1a/1b')
        os.makedirs(tmpdir + '/install/2/2a')
        os.makedirs(tmpdir + '/install/3')
        open(tmpdir + '/install/a', mode='w').close()
        open(tmpdir + '/install/b', mode='w').close()
        open(tmpdir + '/install/1/a', mode='w').close()
        open(tmpdir + '/install/3/a', mode='w').close()

        p.stagedir = tmpdir + '/stage'
        os.makedirs(tmpdir + '/stage/1/1a/1b')
        os.makedirs(tmpdir + '/stage/2/2a')
        os.makedirs(tmpdir + '/stage/2/2b')
        os.makedirs(tmpdir + '/stage/3')
        open(tmpdir + '/stage/a', mode='w').close()
        open(tmpdir + '/stage/b', mode='w').close()
        open(tmpdir + '/stage/c', mode='w').close()
        open(tmpdir + '/stage/1/a', mode='w').close()
        open(tmpdir + '/stage/2/2b/a', mode='w').close()
        open(tmpdir + '/stage/3/a', mode='w').close()

        self.assertEqual(p.collectSnapFiles([], []), (set(), set()))

        self.assertEqual(p.collectSnapFiles(['*'], []), (
            set(['1', '1/1a', '1/1a/1b', '2', '2/2a', '3']),
            set(['a', 'b', '1/a', '3/a'])))

        self.assertEqual(p.collectSnapFiles(['*'], ['1']), (
            set(['2', '2/2a', '3']),
            set(['a', 'b', '3/a'])))

        self.assertEqual(p.collectSnapFiles(['a'], ['*']), (set(), set()))

        self.assertEqual(p.collectSnapFiles(['*'], ['*/*']), (
            set(['1', '2', '3']),
            set(['a', 'b'])))

        self.assertEqual(p.collectSnapFiles(['1', '2'], ['*/a']), (
            set(['1', '1/1a', '1/1a/1b', '2', '2/2a']),
            set()))

    def test_copy_plugin(self):
        mock_options = Mock()
        mock_options.files = {
            "src": "dst",
        }
        c = CopyPlugin("copy", mock_options)

        with patch("snapcraft.common.run") as mock_run:
            c.build()
            wd = os.path.join(os.path.dirname(__file__))
            mock_run.assert_called_with(
                ["cp", "--preserve=all", "src", os.path.join(c.installdir, "dst")], cwd=wd)
