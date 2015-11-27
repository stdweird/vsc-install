import os

from vsc.install import shared_setup
from vsc.install.shared_setup import get_name_url, sanitize

from vsc.install.testing import TestCase

class TestSetup(TestCase):
    """Test shared_setup"""

    def test_get_name_url(self):
        """Test naming function"""
        res = {
            'name': 'vsc-install',
            'url': 'https://github.com/hpcugent/vsc-install',
            'download_url': 'https://github.com/hpcugent/vsc-install/archive/0.1.2.tar.gz',
        }
        for fn in ['PKG-INFO', 'git_config', 'git_config_1', 'git_config_2', 'git_config_3', 'git_config_4', 'git_config_5']:
            self.assertEqual(get_name_url(os.path.join(shared_setup.REPO_TEST_DIR, 'setup', fn), version='0.1.2'), res,
                             msg='determined name and url from %s file' % fn)

        res.pop('download_url')
        fn = 'git_config'
        self.assertEqual(get_name_url(os.path.join(shared_setup.REPO_TEST_DIR, 'setup', fn), version='0.1.2', license_name='LGPLv2+'), res,
                         msg='determined name and url from %s file with license' % fn)

    def test_sanitize(self):
        """Test sanitize function"""
        os.environ['VSC_RPM_PYTHON']='1'
        self.assertEqual(sanitize('anything >= 5'), 'python-anything >= 5',
                         msg='all packages are prefixed with VSC_RPM_PYTHON set')

        self.assertEqual(sanitize('vsc-xyz >= 10'), 'python-vsc-xyz >= 10',
                         msg='vsc packages are prefixed with VSC_RPM_PYTHON set')

        self.assertEqual(sanitize('python-ldap == 11'), 'python-ldap == 11',
                         msg='packages starting with python- are not prefixed again with VSC_RPM_PYTHON set')

        self.assertEqual(shared_setup.PYTHON_BDIST_RPM_PREFIX_MAP, {'pycrypto':'python-crypto'},
                         msg='PYTHON_BDIST_RPM_PREFIX_MAP is hardcoded mapping')
        self.assertEqual(sanitize('pycrypto == 12'), 'python-crypto == 12',
                         msg='packages in PYTHON_BDIST_RPM_PREFIX_MAP are repalced with value with VSC_RPM_PYTHON set')

        self.assertEqual(shared_setup.NO_PREFIX_PYTHON_BDIST_RPM, ['pbs_python'],
                         msg='NO_PREFIX_PYTHON_BDIST_RPM is list of packages that are not modified')
        self.assertEqual(sanitize('pbs_python <= 13'), 'pbs_python <= 13',
                         msg='packages in PYTHON_BDIST_RPM_PREFIX_MAP are not prefixed with VSC_RPM_PYTHON set')

        self.assertEqual(sanitize(['anything >= 5', 'vsc-xyz >= 10', 'pycrypto == 12', 'pbs_python <= 13']),
                         'python-anything >= 5,python-vsc-xyz >= 10,python-crypto == 12,pbs_python <= 13',
                         msg='list is ,-joined and replaced/prefixed with VSC_RPM_PYTHON set')


        os.environ['VSC_RPM_PYTHON']='0'
        self.assertEqual(sanitize('anything >= 5'), 'anything >= 5',
                         msg='no prefixing with VSC_RPM_PYTHON not set')
        self.assertEqual(sanitize('vsc-xyz >= 10'), 'vsc-xyz >= 10',
                         msg='vsc packages are not prefixed with VSC_RPM_PYTHON not set')
        self.assertEqual(sanitize('pycrypto == 12'), 'pycrypto == 12',
                         msg='packages in PYTHON_BDIST_RPM_PREFIX_MAP are not repalced with value with VSC_RPM_PYTHON not set')
        self.assertEqual(sanitize('pbs_python <= 13'), 'pbs_python <= 13',
                         msg='packages in PYTHON_BDIST_RPM_PREFIX_MAP are not prefixed with VSC_RPM_PYTHON not set')


        self.assertEqual(sanitize(['anything >= 5', 'vsc-xyz >= 10', 'pycrypto == 12', 'pbs_python <= 13']),
                         'anything >= 5,vsc-xyz >= 10,pycrypto == 12,pbs_python <= 13',
                         msg='list is ,-joined and nothing replaced/prefixed with VSC_RPM_PYTHON not set')
