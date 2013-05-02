from verwatch.fetch import VersionFetcher
from verwatch.util import run, parse_nvr
import hashlib


class RepoqueryFetcher(VersionFetcher):
    name = 'repoquery'

    def __init__(self, **kwargs):
        VersionFetcher.__init__(self, **kwargs)
        if 'options' not in kwargs:
            raise ValueError("options argument not supplied to repoquery "
                             "fetcher. 'repo_base' option is required.")
        if 'paths' not in kwargs:
            raise ValueError("paths argument not supplied to repoquery "
                             "fetcher.")
        options = kwargs['options']
        if not options or 'repo_base' not in options:
            raise ValueError("'repo_base' option not supplied to repoquery "
                             "fetcher.")
        self.paths = kwargs['paths']
        self.repo_base = options['repo_base']

    def _get_version(self, pkg_name, branch):
        hsh = hashlib.md5()
        hsh.update(self.repo_base)
        hsh.update(branch)
        repoid = "verw_%s" % hsh.hexdigest()
        errc, out, err = run("repoquery "
                         "--repofrompath=%(repoid)s,%(repo_base)s/%(branch)s/ "
                             "--repoid=%(repoid)s -q %(pkg_name)s" % {
                             'repo_base': self.repo_base,
                             'branch': branch,
                             'pkg_name': pkg_name,
                             'repoid': repoid})
        if errc:
            return {'error': err or out}
        if not out:
            return {'error': "No version found."}
        lines = out.strip().split("\n")
        if len(lines) > 1:
            # TODO: Select best version.
            msg = "Got more than 1 version using repoquery... FIXME!"
            raise NotImplementedError(msg)
        return parse_nvr(lines[0], pkg_name)
