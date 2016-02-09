#
# Copyright 2014-2016 Ghent University
#
# This file is part of vsc-install,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/hpcugent/vsc-install
#
# vsc-install is free software: you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation, either version 2 of
# the License, or (at your option) any later version.
#
# vsc-install is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with vsc-install. If not, see <http://www.gnu.org/licenses/>.
#
"""
Module for common project tests

CommonTest usage: make a module 00-import.py in the test/ dir that has only the following line
   from vsc.install.commontest import CommonTest

Running python setup.py test will pick this up and do its magic

@author: Stijn De Weirdt (Ghent University)
"""
import io
import logging
import optparse
import os
import pprint
import re
import sys

from distutils import log
from vsc.install.shared_setup import generate_packages, generate_scripts, generate_modules, \
    FILES_IN_PACKAGES, REPO_BASE_DIR, README
from vsc.install.headers import check_header
from vsc.install.testing import TestCase

# No prospector in py26 or earlier
# Also not enforced on installation
HAS_PROTECTOR = False
Prospector = None
ProspectorConfig = None

HAS_RENDERER = False
render = None

if sys.version_info >= (2, 7):
    # Do not even try on py26
    try:
        _old_basicconfig = logging.basicConfig
        from prospector.run import Prospector
        from prospector.config import ProspectorConfig
        HAS_PROTECTOR = True
        # restore in case pyroma is missing (see https://github.com/landscapeio/prospector/pull/156)
        logging.basicConfig = _old_basicconfig
    except ImportError:
        pass

try:
    from readme_renderer.rst import render
    HAS_RENDERER = True
except ImportError:
    pass


class CommonTest(TestCase):
    """
    Test class to group common basic tests such as
        - can a module/script be imported
        - simple prospector test
    """

    EXTRA_PKGS = None # additional packages to test / try to import
    EXCLUDE_PKGS = None # list of regexp patters to remove from list of package to test

    EXTRA_MODS = None # additional modules to test / try to import
    EXCLUDE_MODS = None # list of regexp patterns to remove from list of modules to test

    EXTRA_SCRIPTS = None # additional scripts to test / try to import
    EXCLUDE_SCRIPTS = None # list of regexp patterns to remove from list of scripts to test

    CHECK_HEADER = True

    # List of regexps patterns applied to code or message of a prospector.message.Message
    #   Blacklist: if match, skip message, do not check whitelist
    #   Whitelist: if match, fail test
    PROSPECTOR_BLACKLIST = [
    ]
    PROSPECTOR_WHITELIST = [
        'undefined',
    ]

    # Prospector commandline options (positional path is added automatically)
    PROSPECTOR_OPTIONS = [
        '--strictness', 'verylow',
        '--max-line-length', '120',
        '--absolute-paths',
    ]

    def setUp(self):
        """Cleanup after running a test."""
        self.orig_sys_argv = sys.argv
        super(CommonTest, self).setUp()

    def tearDown(self):
        """Cleanup after running a test."""
        sys.argv = self.orig_sys_argv
        super(CommonTest, self).tearDown()

    def _import(self, pkg):
        try:
            __import__(pkg)
        except ImportError as e:
            log.warn('Import of %s failed with %s' % (pkg, e))

        self.assertTrue(pkg in sys.modules, msg='import %s was success' % pkg)

    def test_import_packages(self):
        """Try to import each namespace"""
        for pkg in generate_packages(extra=self.EXTRA_PKGS, exclude=self.EXCLUDE_PKGS):
            self._import(pkg)

            if self.CHECK_HEADER:
                for fn in FILES_IN_PACKAGES['packages'][pkg]:
                    self.assertFalse(check_header(os.path.join(REPO_BASE_DIR, fn), script=False, write=False),
                                     msg='check_header of %s' % fn)

    def test_import_modules(self):
        """Try to import each module"""
        for modname in generate_modules(extra=self.EXTRA_MODS, exclude=self.EXCLUDE_MODS):
            self._import(modname)

    def test_importscripts(self):
        """Try to import each python script as a module"""
        # sys.path is already setup correctly
        for scr in generate_scripts(extra=self.EXTRA_SCRIPTS, exclude=self.EXCLUDE_SCRIPTS):
            if not scr.endswith('.py'):
                continue
            self._import(os.path.basename(scr)[:-len('.py')])

            if self.CHECK_HEADER:
                self.assertFalse(check_header(os.path.join(REPO_BASE_DIR, scr), script=True, write=False),
                                 msg='check_header of %s' % scr)

    def test_prospector(self):
        """Run prospector.run.main, but apply white/blacklists to the results"""
        orig_expand_default = optparse.HelpFormatter.expand_default

        if not HAS_PROTECTOR:
            if sys.version_info < (2, 7):
                log.info('No protector tests are ran on py26 or older.')
            else:
                log.info('No protector tests are ran, install prospector manually first')

                # This is fatal on jenkins/...
                if 'JENKINS_URL' in os.environ:
                    self.assertTrue(False, 'prospector must be installed in jenkins environment')

            return

        sys.argv = ['fakename']
        sys.argv.extend(self.PROSPECTOR_OPTIONS)
        # add/set REPO_BASE_DIR as positional path
        sys.argv.append(REPO_BASE_DIR)

        config = ProspectorConfig()
        prospector = Prospector(config)

        prospector.execute()

        blacklist = map(re.compile, self.PROSPECTOR_BLACKLIST)
        whitelist = map(re.compile, self.PROSPECTOR_WHITELIST)

        failures = []
        for msg in prospector.get_messages():
            # example msg.as_dict():
            #  {'source': 'pylint', 'message': 'Missing function docstring', 'code': 'missing-docstring',
            #   'location': {'function': 'TestHeaders.test_check_header.lgpl', 'path': u'headers.py',
            #                'line': 122, 'character': 8, 'module': 'headers'}}
            log.debug("prospector message %s" % msg.as_dict())

            if any([bool(reg.search(msg.code) or reg.search(msg.message)) for reg in blacklist]):
                continue

            if any([bool(reg.search(msg.code) or reg.search(msg.message)) for reg in whitelist]):
                failures.append(msg.as_dict())

        # There is some ugly monkeypatch code in pylint
        #     (or logilab if no recent enough pylint is installed)
        # Make sure the original is restored
        # (before any errors are reported; no need to put this in setUp/tearDown)
        optparse.HelpFormatter.expand_default = orig_expand_default

        self.assertFalse(failures, "prospector failures: %s" % pprint.pformat(failures))

    def test_readme_renderer(self):
        """
        The README has to render properly.
        """

        if not HAS_RENDERER:
            log.info('No README render tests are ran, install readme_renderer manually first')

            # This is fatal on jenkins/...
            if 'JENKINS_URL' in os.environ:
                self.assertTrue(False, 'readme_renderer must be installed in jenkins environment')

            return

        # inspired by the check -rs command readme_renderer.integration.distutils

        # existence of README is checked in shared_setup
        readme = os.path.join(REPO_BASE_DIR, README)
        data = open(readme).read()
        stream = io.StringIO()
        markup = render(data, stream=stream)

        failures = []
        for line in stream.getvalue().splitlines():
            if line.startswith("<string>"):
                line = line[8:]
            failures.append(line)

        self.assertFalse(failures, "readme_renderer failures: %s" % pprint.pformat(failures))

        if markup is None:
            self.assertTrue(False, "Invalid markup which will not be rendered on PyPI.")
