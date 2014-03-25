#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# cnu.py - Copyright (C) 2014 Red Hat, Inc.
# Written by Fabian Deutsch <fabiand@fedoraproject.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.  A copy of the GNU General Public License is
# also available at http://www.gnu.org/copyleft/gpl.html.

from verwatch.fetch import VersionFetcher
from verwatch.util import parse_nvr
import re
from cnucnu.package_list import Repository, Package


class CnucnuFetcher(VersionFetcher):
    """Get a version from a URL

    Args:
        regex: Regexp to find the NVR in the page. %s is substituted
               by the pkg_name
    """
    name = 'cnucnu'
    regex = '(%(pkg_name)s-[\d.]+-[\d.]+)\..*'
    url_base = ""

    def __init__(self, **kwargs):
        VersionFetcher.__init__(self, **kwargs)
        if 'options' in kwargs:
            options = kwargs['options']
            if 'regex' in options:
                self.regex = options['regex']
        if not options or 'url_base' not in options:
            raise ValueError("'url_base' option not supplied to cnucnu "
                             "fetcher.")
        self.url_base = options['url_base']


    def _get_version(self, pkg_name, branch):
        ver = {}
        args = {"pkg_name": pkg_name, "branch": branch}
        try:
            repo = Repository()
            p = Package(pkg_name, None, None, repo)
            p.url = self.url_base % args
            p.regex = self.regex % args
            #print (p.name, p.upstream_versions, p.latest_upstream)
            p.upstream_versions
        except Exception as e:
            ver['error'] = str(e)
            ver['error'] += ' - Bad regex or URL?'
            return ver
        nvr = parse_nvr(p.latest_upstream, pkg_name)
        ver.update(nvr)
        return ver

if __name__ == "__main__":
    repo = Repository()
    p = Package("ovirt-node", None, None, repo)
    p.url = "http://plain.resources.ovirt.org/pub/ovirt-node-base-stable/rpm/el6/noarch/"
    p.regex = r"(%s-[\d.]+-[\d.]+)\..*" % p.name
    print (p.name, p.upstream_versions, p.latest_upstream)

    f = CnucnuFetcher()
    print (f._get_version(p.name, p.url + "/$(branch)"))
