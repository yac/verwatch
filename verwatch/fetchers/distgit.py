from verwatch.fetch import VersionFetcher
from verwatch.fetchers.git import GitFetcher
from verwatch.util import run, is_version
import rpm
import os
import re


class DistGitFetcher(GitFetcher):
    name = 'distgit'

    def _checkout(self, branch):
        self.cmd = 'git checkout "%s"' % branch
        errc, out, err = run(self.cmd)
        if errc:
            raise RuntimeError("git checkout failed: %s" % err or out)
        self.cmd = 'git pull'
        errc, out, err = run(self.cmd)
        if errc:
            raise RuntimeError("git pull failed: %s" % err or out)

    def _get_version(self, pkg_name, branch):
        self.cmd = None
        try:
            self._prepare_repo(pkg_name)
            self._checkout(branch)
        except RuntimeError, e:
            return {'error': e.args[0], 'cmd': self.cmd}

        specs = [f for f in os.listdir('.') \
                if os.path.isfile(f) and f.endswith('.spec')]
        if not specs:
            return {'error': "No .spec files found."}
        if len(specs) != 1:
            return {'error': "Multiple .spec files present."}
        spec_fn = specs[0]
        try:
            spec = rpm.ts().parseSpec(spec_fn)
        except ValueError, e:
            return {'error': "Error parsing '%s': %s" % (spec_fn, e.args[0])}
        ver = {
            'version': spec.sourceHeader['version'],
            'release': spec.sourceHeader['release'],
        }
        if 'epoch' in spec.sourceHeader:
            ver['epoch'] = int(spec.sourceHeader['epoch'])
        return ver
