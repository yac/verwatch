from verwatch.fetch import VersionFetcher
from verwatch.util import run, parse_nvr
import re


class KojiFetcher(VersionFetcher):
    name = 'koji'

    def __init__(self, **kwargs):
        VersionFetcher.__init__(self, **kwargs)
        self.command = 'koji'
        if 'options' in kwargs:
            options = kwargs['options']
            if 'command' in options:
                self.command = options['command']

    def _koji_get_version(self, pkg_name, branch):
        ver = {}
        cmd = "%s latest-pkg \"%s\" \"%s\"" % (self.command, branch, pkg_name)
        ver['cmd'] = cmd
        errc, out, err = run(cmd)
        if errc:
            ver['error'] = err or out
            return ver
        lines = out.strip().split("\n")[2:]
        if not lines:
            ver['error'] = 'No results. Bad package name?'
            return ver
        if len(lines) > 1:
            ver['error'] = \
                    "`%s latest-pkg` returned more than one result. WAT?" \
                    % self.command
            return ver
        line = lines[0]
        cols = re.split(' +', line)
        if len(cols) == 1:
            ver['error'] = '%s output parsing failed: %s' % (self.command,
                                                             line)
            return ver
        nvr = parse_nvr(cols[0], pkg_name)
        ver.update(nvr)
        return ver

    def _get_version(self, pkg_name, branch):
        ver = self._koji_get_version(pkg_name, branch)
        if self.command == 'brew':
            next_branch = "%s-candidate" % branch
        else:
            next_branch = "%s-updates-candidate" % branch
        next_ver = self._koji_get_version(pkg_name, next_branch)
        if 'version' in next_ver:
            ver['next'] = next_ver
        return ver
