from verwatch.fetch import VersionFetcher
from verwatch.util import run
import os


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
        self.repo_base_dir = "%s/%s/%s" % (self.paths.cache_dir, self.name,
                                           options['id'])
        if not os.path.isdir(self.repo_base_dir):
            os.makedirs(self.repo_base_dir)
        self.cmd = None

    def _clone_repo(self, pkg_name):
        os.chdir(self.repo_base_dir)
        repo_url = '%s%s.git' % (self.repo_base, pkg_name)
        self.cmd = 'git clone "%s"' % repo_url
        errc, out, err = run(self.cmd)
        if errc:
            raise RuntimeError("git clone failed: %s" % err)

    def _prepare_repo(self, pkg_name):
        """
        Clone/fetch repo and chdir into it.
        """
        repo_dir = "%s/%s" % (self.repo_base_dir, pkg_name)
        if os.path.isdir(repo_dir):
            os.chdir(repo_dir)
            self.cmd = 'git fetch --all'
            errc, out, err = run(self.cmd)
            if errc:
                return {'error': 'git fetch failed: %s' % (err or out),
                        'cmd': self.cmd}
        else:
            self._clone_repo(pkg_name)
            os.chdir(repo_dir)

    def _get_version(self, pkg_name, branch):
        try:
            self._prepare_repo(pkg_name)
        except RuntimeError, e:
            return {'error': e.args[0], 'cmd': self.cmd}
        ver = {}
        self.cmd = 'git describe --abbrev=0 --tags origin/%s' % branch
        ver['cmd'] = self.cmd
        errc, out, err = run(self.cmd)
        if errc:
            err_msg = err or out
            if err_msg.find("Not a valid object name") >= 0:
                err_msg = "Branch '%s' doesn't seem to exist." % branch
            else:
                err_msg = 'git log failed: %s' % err_msg
            ver['error'] = err_msg
            return ver
        v = out.lstrip('v').rstrip()
        if v:
            ver['version'] = v
        else:
            ver['error'] = "No git tags found in repo."
        return ver
