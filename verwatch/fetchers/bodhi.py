from verwatch.fetch import VersionFetcher
from verwatch.util import run, parse_nvr
import re


class BodhiFetcher(VersionFetcher):
    name = 'bodhi'

    def __init__(self, **kwargs):
        VersionFetcher.__init__(self, **kwargs)
        self.cache = {}

    def _get_version(self, pkg_name, branch):
        ver = {}
        cmd = 'bodhi -L %s' % pkg_name
        ver['cmd'] = cmd
        if pkg_name not in self.cache:
            errc, out, err = run(cmd)
            if errc:
                ver['error'] =  err or out
                return ver
            if not out:
                ver['error'] = 'No version returned.'
                return ver
            pkg_vers = {}
            for line in out.rstrip().split('\n'):
                line = line.strip()
                br, nvr = re.split(' +', line)
                pkg_vers[br] = parse_nvr(nvr, pkg_name)
            self.cache[pkg_name] = pkg_vers
        pkg_vers = self.cache[pkg_name]
        if branch in pkg_vers:
            ver.update(pkg_vers[branch])
        else:
            ver['error'] = "Tag not found."
        testing_branch = "%s-testing" % branch
        if testing_branch in pkg_vers:
            ver['next'] = pkg_vers[testing_branch]
            ver['next']['cmd'] = cmd
        return ver
