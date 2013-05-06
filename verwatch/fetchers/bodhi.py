from verwatch.fetch import VersionFetcher
from verwatch.util import run, parse_nvr
import re


class BodhiFetcher(VersionFetcher):
    name = 'bodhi'

    def __init__(self, **kwargs):
        VersionFetcher.__init__(self, **kwargs)
        self.cache = {}

    def _get_version(self, pkg_name, branch):
        if pkg_name not in self.cache:
            errc, out, err = run('bodhi -L %s' % pkg_name)
            if errc:
                return {'error': err or out}
            if not out:
                return {'error': 'No version returned.'}
            pkg_vers = {}
            for line in out.rstrip().split('\n'):
                line = line.strip()
                br, nvr = re.split(' +', line)
                pkg_vers[br] = parse_nvr(nvr, pkg_name)
            self.cache[pkg_name] = pkg_vers
        pkg_vers = self.cache[pkg_name]
        if branch not in pkg_vers:
            return {'error': "Tag not found."}
        ver = pkg_vers[branch]
        testing_branch = "%s-testing" % branch
        if testing_branch in pkg_vers:
            ver['next'] = pkg_vers[testing_branch]
        return ver
