from verwatch.fetch import VersionFetcher
from verwatch.util import run, is_version
import os
import re


class GitFetcher(VersionFetcher):
    name = 'git'

    def __init__(self, **kwargs):
        VersionFetcher.__init__(self, **kwargs)
        if 'options' not in kwargs:
            raise ValueError("options argument not supplied to git fetcher. "
                             "'repo_base' option is required.")
        if 'paths' not in kwargs:
            raise ValueError("paths argument not supplied to git fetcher.")
        options = kwargs['options']
        if not options or 'repo_base' not in options:
            raise ValueError("'repo_base' option not supplied to git fetcher.")
        if not options or 'id' not in options:
            raise RuntimeError("'id' option not supplied to git fetcher. "
                             "verwatch is supposed to supply this internally.")
        self.paths = kwargs['paths']
        self.repo_base = options['repo_base']
        # 'id' is supplied by verwatch
        self.repo_base_dir = "%s/git/%s" % (self.paths.cache_dir, options['id']
                                           )
        if not os.path.isdir(self.repo_base_dir):
            os.makedirs(self.repo_base_dir)

    def _clone_repo(self, pkg_name):
        os.chdir(self.repo_base_dir)
        repo_url = '%s%s.git' % (self.repo_base, pkg_name)
        errc, out, err = run('git clone "%s"' % repo_url)
        if errc:
            raise RuntimeError("git clone failed: %s" % err)

    def _get_version(self, pkg_name, branch):
        repo_dir = "%s/%s" % (self.repo_base_dir, pkg_name)
        if os.path.isdir(repo_dir):
            os.chdir(repo_dir)
            errc, out, err = run('git fetch --all')
            if errc:
                return {'error': 'git fetch failed: %s' % (err or out)}
        else:
            try:
                self._clone_repo(pkg_name)
            except RuntimeError, e:
                return {'error': e.args[0]}
            os.chdir(repo_dir)
        ver = {}
        cmd = ('git log --tags --simplify-by-decoration '
               '--pretty="format:%%d" origin/%s' % branch)
        ver['cmd'] = cmd
        errc, out, err = run(cmd)
        if errc:
            err_msg = err or out
            if err_msg.find("unknown revision") >= 0:
                err_msg = "Branch '%s' doesn't seem to exist." % branch
            else:
                err_msg = 'git log failed: %s' % err_msg
            ver['error'] = err_msg
            return ver
        # dark parsing magic, move along
        tags = out.rstrip().split('\n')
        tags = map(lambda s: re.split(', ', s.lstrip(' (').rstrip(') ')), tags)
        tags = filter(is_version, [tag for taglist in tags for tag in taglist])
        if tags:
            ver['version'] = tags[0]
        else:
            ver['error'] = "No git tags found in repo."
        return ver
