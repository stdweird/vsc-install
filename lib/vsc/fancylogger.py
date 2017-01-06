#
# Copyright 2015-2017 Ghent University
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
"""
vsc.fancylogger has been deprecated since forever,
vsc.utils.fancylogger should be used instead.

This module provides a migration path away from vsc.fancylogger:
  vsc.fancylogger currently provided by vsc-base, wherever it is used, vsc-base is present
  we start with tracking actual leftover usage
  any code that uses it, should receives updates to use vsc.utils.fancylogger
  in the 1.0.1 release, this file should not be shipped anymore
    (and only requires an update of vsc-install)

At least 'import vsc' can be used now without triggering an import of fancylogger
"""

# it's ok if this fails with only vsc-install installed.
# we cannot introduce a dependency on vsc-base (and we do not care)
from vsc.utils.fancylogger import *
# (re)import these not to confuse pylint (otherwsie seen as undefined)
from vsc.utils.fancylogger import logToDevLog, getLogger

# Deprecation tracker to syslog
logToDevLog(True)
getLogger().error("LEGACYVSCFANCYLOGGER from %s %s", __name__, globals().get('__file__','<nofile>'))
logToDevLog(False)
