from verwatch.util import VersionFetcher, run, vr
import re


class FedoraFetcher(VersionFetcher):
    def __init__(self, paths=None, options=None):
        self.cache = {}

    def get_version(self, pkg_name, branch):
        if pkg_name not in self.cache:
            errc, out, err = run('bodhi -L %s' % pkg_name)
            if errc:
                return {'error': err or out}
            pkg_vers = {}
            for line in out.rstrip().split('\n'):
                line = line.lstrip().rstrip()
                branch, nvr = re.split(' +', line)
                v, r = vr(nvr, pkg_name)
                pkg_vers[branch] = {'version': v, 'release': r}
            self.cache[pkg_name] = pkg_vers
        pkg_vers = self.cache[pkg_name]
        if branch not in pkg_vers:
            return {'error': "Tag not found."}
        ver = pkg_vers[branch]
        testing_branch = "%s-testing" % branch
        if testing_branch in pkg_vers:
            ver['next'] = pkg_vers[testing_branch]
        return ver


# Following is a relic working with koji, might or might not be useful.
#def fetch_version_fedora(pkg_name, branch):
    #cmd = "koji latest-pkg \"%s\" \"%s\"" % (branch, pkg_name)
    #errc, out, err = run(cmd)
    #out = out.rstrip()
    #if errc:
        #return {'error': out}
    #line = out.split('\n')[-1]
    #if line.find('-------') == 0:
        #return {'error': 'No results. Bad package name?'}
    #m = re.match('^%s-([^ ]+) .*$' % re.escape(pkg_name), line)
    #if not m:
        #return {'error': 'Koji output parsing failed: %s' % line}
    #vr = m.group(1)
    #return {'version': vr}
