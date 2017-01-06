#
# Copyright 2017-2017 Ghent University
#
# This file is part of vsc-install,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
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
#
# Copyright 2016-2016 Ghent University
#
# This file is part of vsc-install,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
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
import os
import re

from vsc.install import shared_setup
from vsc.install.shared_setup import action_target, vsc_setup, _fvs

from vsc.install.testing import TestCase


class TestSetup(TestCase):
    """Test shared_setup"""

    def setUp(self):
        """create a self.setup.instance for every test"""
        super(TestSetup, self).setUp()
        self.setup = vsc_setup()

    def test_get_name_url(self):
        """Test naming function"""
        res = {
            'name': 'vsc-install',
            'url': 'https://github.com/hpcugent/vsc-install',
            'download_url': 'https://github.com/hpcugent/vsc-install/archive/0.1.2.tar.gz',
        }
        for fn in ['PKG-INFO', 'git_config', 'git_config_1', 'git_config_2', 'git_config_3', 'git_config_4',
                   'git_config_5']:
            self.assertEqual(self.setup.get_name_url(os.path.join(self.setup.REPO_TEST_DIR, 'setup', fn),
                             version='0.1.2'), res,
                             msg='determined name and url from %s file' % fn)

        res.pop('download_url')
        fn = 'git_config'
        self.assertEqual(self.setup.get_name_url(os.path.join(self.setup.REPO_TEST_DIR, 'setup', fn), version='0.1.2',
                         license_name='LGPLv2+'), res,
                         msg='determined name and url from %s file with license' % fn)

    def test_sanitize(self):
        """Test sanitize function"""
        os.environ['VSC_RPM_PYTHON'] = '1'
        self.assertEqual(self.setup.sanitize('anything >= 5'), 'python-anything >= 5',
                         msg='all packages are prefixed with VSC_RPM_PYTHON set')

        self.assertEqual(self.setup.sanitize('vsc-xyz >= 10'), 'python-vsc-xyz >= 10',
                         msg='vsc packages are prefixed with VSC_RPM_PYTHON set')

        self.assertEqual(self.setup.sanitize('python-ldap == 11'), 'python-ldap == 11',
                         msg='packages starting with python- are not prefixed again with VSC_RPM_PYTHON set')

        self.assertEqual(shared_setup.PYTHON_BDIST_RPM_PREFIX_MAP, {'pycrypto': 'python-crypto'},
                         msg='PYTHON_BDIST_RPM_PREFIX_MAP is hardcoded mapping')
        self.assertEqual(self.setup.sanitize('pycrypto == 12'), 'python-crypto == 12',
                         msg='packages in PYTHON_BDIST_RPM_PREFIX_MAP are repalced with value with VSC_RPM_PYTHON set')

        self.assertEqual(shared_setup.NO_PREFIX_PYTHON_BDIST_RPM, ['pbs_python'],
                         msg='NO_PREFIX_PYTHON_BDIST_RPM is list of packages that are not modified')
        self.assertEqual(self.setup.sanitize('pbs_python <= 13'), 'pbs_python <= 13',
                         msg='packages in PYTHON_BDIST_RPM_PREFIX_MAP are not prefixed with VSC_RPM_PYTHON set')

        self.assertEqual(self.setup.sanitize(['anything >= 5', 'vsc-xyz >= 10', 'pycrypto == 12', 'pbs_python <= 13']),
                         'python-anything >= 5,python-vsc-xyz >= 10,python-crypto == 12,pbs_python <= 13',
                         msg='list is ,-joined and replaced/prefixed with VSC_RPM_PYTHON set')

        os.environ['VSC_RPM_PYTHON'] = '0'
        self.assertEqual(self.setup.sanitize('anything >= 5'), 'anything >= 5',
                         msg='no prefixing with VSC_RPM_PYTHON not set')
        self.assertEqual(self.setup.sanitize('vsc-xyz >= 10'), 'vsc-xyz >= 10',
                         msg='vsc packages are not prefixed with VSC_RPM_PYTHON not set')
        self.assertEqual(self.setup.sanitize('pycrypto == 12'), 'pycrypto == 12',
                         msg='packages in PYTHON_BDIST_RPM_PREFIX_MAP are not repalced with value with VSC_RPM_PYTHON'
                         'not set')
        self.assertEqual(self.setup.sanitize('pbs_python <= 13'), 'pbs_python <= 13',
                         msg='packages in PYTHON_BDIST_RPM_PREFIX_MAP are not prefixed with VSC_RPM_PYTHON not set')
        self.assertEqual(self.setup.sanitize(['anything >= 5', 'vsc-xyz >= 10', 'pycrypto == 12', 'pbs_python <= 13']),
                         'anything >= 5,vsc-xyz >= 10,pycrypto == 12,pbs_python <= 13',
                         msg='list is ,-joined and nothing replaced/prefixed with VSC_RPM_PYTHON not set')

    def test_rel_gitignore(self):
        """
        Test the rel_gitignore function
        it should fail, since we don't specify a path for .pyc files in our gitignore
        """
        # when testing with a base_dir that has a .git folder, and a .gitignore file, we should get an error mentioning
        # .pyc
        base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), './testdata')
        try:
            self.setup.rel_gitignore(['testdata'], base_dir=base_dir)
        except Exception as e:
            self.assertTrue('.pyc' in e.message, msg=e)
        else:
            self.assertTrue(False, 'rel_gitignore should have raised an exception, but did not!')
        # it should not fail if base_dir does not contain a .git folder
        base_dir = os.path.dirname(os.path.realpath(__file__))
        self.assertEqual(self.setup.rel_gitignore(['testdata'], base_dir=base_dir), ['../testdata'])

    def test_import(self):
        """Test importing things from shared_setup.py, these should not be broken for backward compatibility."""
        from vsc.install.shared_setup import SHARED_TARGET
        from vsc.install.shared_setup import ag, eh, jt, kh, kw, lm, sdw, wdp, wp

    def test_action_target(self):
        """Test action_target function, mostly w.r.t. backward compatibility."""
        def fake_setup(*args, **kwargs):
            """Fake setup function to test action_target with."""
            print 'args: ', args
            print 'kwargs:', kwargs

        self.mock_stdout(True)
        action_target({'name': 'vsc-test'}, setupfn=fake_setup)
        txt = self.get_stdout()
        self.mock_stdout(False)

        self.assertTrue(re.search(r"^args:\s*\(\)", txt, re.M))
        self.assertTrue(re.search(r"^kwargs:\s*\{.*'name':\s*'vsc-test'", txt, re.M))

        self.mock_stdout(True)
        action_target({'name': 'vsc-test'}, setupfn=fake_setup, urltemplate='http://example.com/%(name)s')
        txt = self.get_stdout()
        self.mock_stdout(False)
        self.assertTrue(re.search(r"^args:\s*\(\)", txt, re.M))
        self.assertTrue(re.search(r"^kwargs:\s*\{.*'url':\s*'http://example.com/vsc-test'", txt, re.M))

    def test_prepare_rpm(self):
        """
        Test the prepare rpm function
        especially in effect to generating correct package list wrt excluded_pkgs_rpm
        """
        package = {
            'name': 'vsc-test',
            'excluded_pkgs_rpm': [],
        }
        setup = vsc_setup()

        libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), './testdata')
        setup.REPO_LIB_DIR = libdir
        setup.prepare_rpm(package)
        self.assertEqual(setup.SHARED_TARGET['packages'], ['vsc', 'vsc.test'])
        package = {
            'name': 'vsc-test',
            'excluded_pkgs_rpm': ['vsc', 'vsc.test'],
        }
        setup = vsc_setup()
        setup.REPO_LIB_DIR = libdir
        setup.prepare_rpm(package)
        self.assertEqual(setup.SHARED_TARGET['packages'], ['vsc', 'vsc.test'])

    def test_parse_target(self):
        """Test for parse target"""
        package = {
            'name': 'vsc-test',
            'excluded_pkgs_rpm': [],
        }
        setup = vsc_setup()
        klass = _fvs('vsc_bdist_rpm egg_info')
        # test to see if we don't fail on unknown/new cmdclasses
        orig_target = klass.SHARED_TARGET
        klass.SHARED_TARGET['cmdclass']['easy_install'] = object
        new_target = setup.parse_target(package)
        self.assertEquals(new_target['name'], 'vsc-test')
        klass.SHARED_TARGET = orig_target


