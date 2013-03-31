from verwatch.fetch import VersionFetcher
from verwatch.util import run, is_version
import os
import re


class GitFetcher(VersionFetcher):
    name = 'git'

    def __init__(self, paths, options=None):
        if not options or 'repo_base' not in options:
            raise ValueError("'repo_base' option not supplied to git fetcher.")
        self.paths = paths
        self.repo_base = options['repo_base']
        self.repo_base_dir = "%s/%s" % (paths.cache_dir, options['id'])
        if not os.path.isdir(self.repo_base_dir):
            os.makedirs(self.repo_base_dir)

    def _clone_repo(self, pkg_name):
        os.chdir(self.repo_base_dir)
        repo_url = '%s%s.git' % (self.repo_base, pkg_name)
        errc, out, err = run('git clone "%s"' % repo_url)
        if errc:
            raise RuntimeError("git clone failed: %s" % err)

    def get_version(self, pkg_name, branch):
        repo_dir = "%s/%s" % (self.repo_base_dir, pkg_name)
        if os.path.isdir(repo_dir):
            os.chdir(repo_dir)
            errc, out, err = run('git pull')
        else:
            self._clone_repo(pkg_name)
            os.chdir(repo_dir)
        errc, out, err = run('git log --tags --simplify-by-decoration --pretty="format:%d"')
        # dark parsing magic, move along
        tags = out.rstrip().split('\n')
        tags = map(lambda s: re.split(', ', s.lstrip(' (').rstrip(') ')), tags)
        tags = filter(is_version, [tag for taglist in tags for tag in taglist])
        if tags:
            ver = {'version': tags[0]}
        else:
            ver = {'error': "No git tags found in repo."}
        return ver
