# license block
"""
Generate and verify headers from scripts and modules

@author: Stijn De Weirdt (Ghent University)
"""

import os
import re

from datetime import date
from vsc.install.shared_setup import get_license, get_name_url, log

HEADER_REGEXP = re.compile(r'\A(.*?)^(?:\'\'\'|"""|### END OF HEADER)', re.M | re.S)


# tools to determine current header
# generate new header based on license
# allow easy tool to fixup headers

def get_header(filename, script=False):
    """
    Given filename, retrieve header.
    If script is true, retrieve the shebang

    Header is start of file up to (not incl)
        docstring (first 3 ' or " at begin of line)
        magic comment '### END OF HEADER' at begin of line
    Anything can be part of the header, does not require starting # or something like that

    Return tuple: first element is header, 2nd element shebang if script
    """

    if not os.path.isfile(filename):
        raise Exception('get_header filename %s not found' % filename)

    txt = open(filename).read()

    blocks = HEADER_REGEXP.split(txt)
    if len(blocks) == 1:
        # no headers, fake blocks with empty header
        blocks = ['', '']
    elif blocks[0] != '':
        # the block before the begin of text is always empty
        raise Exception('unexpected non-emtpy block with get_header %s: %s' % (filename, blocks))

    header = blocks[1]

    shebang = None
    if script:
        lines = header.split("\n")
        if lines[0].startswith('#!/'):
            shebang = lines[0]
            header = "\n".join(lines[1:])

    return header, shebang


def gen_license_header(license, **kwargs):
    """
    Create an appropriate license header for this project

    license is the license to use
    kwargs is a dict with templating data
        beginyear: copyright beginyear
        endyear: copyright endyear
        name: project name
        url: project url
    """
    template_name = "%s_TEMPLATE" % license.replace('+', '_plus_')
    template = globals().get(template_name, None)
    if template is None:
        raise Exception('gen_license_header cannot find template name %s' % template_name)

    return template.format(**kwargs)


def _this_year():
    """Simple wrapper around date.today().year for unittesting"""
    return date.today().year


def begin_end_from_header(header):
    """
    Return begin and endyear from header.

    Begin is extracted from begin of copyright
    End is current year
    """
    thisyear = _this_year()
    endyear = thisyear

    reg_begin_endyear = re.search(r'^#\s*Copyright\s+(?P<beginyear>\d+)(?:-(?P<endyear>\d+))?($|\s+)', header, re.M)
    if reg_begin_endyear:
        beginyear = int(reg_begin_endyear.groupdict()['beginyear'])
    else:
        log.error('No begin/endyear found, using this year as begin (and end)')
        beginyear = thisyear

    return beginyear, endyear


def _write(filename, content):
    """Simple wrapper around open().write for unittesting"""
    fh = open(filename, 'w')
    fh.write(content)
    fh.close()


def fixup_header(filename, script=False, write=False):
    """
    Given filename, extract the header, verify it

    if write: adapt file to new header

    Return if header is different from expected or not
    """

    header, shebang = get_header(filename, script=script)
    header_end_pos = len(header)
    if shebang is not None:
        header_end_pos += 1 + len(shebang) # 1 is from splitted newline


    # genheader
    name_url = get_name_url()
    license, _ = get_license()

    # begin and endyear from copyright rule
    beginyear, endyear = begin_end_from_header(header)

    data = {
        'beginyear': beginyear,
        'endyear': endyear,
        'name': name_url['name'],
        'url': name_url['url'],
    }

    gen_header = gen_license_header(license, **data)

    changed = gen_header != header

    if write and changed:
        log.info('write enabled and different header. going to modify file %s' % filename)
        wholetext = open(filename).read()
        newtext = ''
        if shebang is not None:
            newtext += shebang + "\n"
        newtext += gen_header
        newtext += wholetext[header_end_pos:]
        _write(filename, newtext)

    # return different or not
    return changed

#
# Only template headers below
#

LGPLv2_plus__TEMPLATE = """#
# Copyright {beginyear}-{endyear} Ghent University
#
# This file is part of {name},
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# {url}
#
# {name} is free software: you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation, either version 2 of
# the License, or (at your option) any later version.
#
# {name} is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with {name}. If not, see <http://www.gnu.org/licenses/>.
#
"""

GPLv2_TEMPLATE = """#
# Copyright {beginyear}-{endyear} Ghent University
#
# This file is part of {name},
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# {url}
#
# {name} is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# {name} is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with {name}.  If not, see <http://www.gnu.org/licenses/>.
#
"""