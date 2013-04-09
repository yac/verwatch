# -*- encoding: utf-8 -*-

import verwatch.conf
import verwatch.util
import verwatch.builtin_fetchers
import verwatch.fetch

import os
import re
import json
import blessings


VERSION = '0.1'
T = blessings.Terminal()


class FetcherManager(object):
    def __init__(self, repo_conf, paths):
        self.fchs = {}
        for fch_name, fch in repo_conf.items():
            fch_cls = fch['fetcher']
            if fch_cls not in verwatch.fetch.VersionFetcher.fetchers:
                raise NotImplementedError("Version fetcher '%s' is not available." % fch_cls)
            fcls = verwatch.fetch.VersionFetcher.fetchers[fch_cls]
            options=fch.get('options', {})
            options['id'] = fch_name
            self.fchs[fch_name] = fcls(paths=paths,
                                       options=options,
                                       alter_pkg_name=fch.get('alter_pkg_name'))

    def fetch_version(self, repo, pkg, branch):
        if repo not in self.fchs:
            raise ValueError("Repo '%s' not configured but referenced by '%s'." % (repo, pkg))
        return self.fchs[repo].get_version(pkg, branch)


class UberPrinter(object):
    def __init__(self, prefix='', indent_cols=4):
        self.prefix = prefix
        self.indent_cols = indent_cols
        self.indent = 0
        self.indent_str = ''

    def shift(self, n):
        self.indent += n
        self.indent_str = self.indent * self.indent_cols * ' '

    def puts(self, pstr, shift=0):
        print "%s%s%s" % (self.prefix, self.indent_str, str(pstr))
        if shift:
            self.shift(shift)


def fetch_versions(pkg_conf, paths):
    pp = UberPrinter(T.yellow('[fetch] '))
    pp.puts("Fetching versions of %s packages:" % len(pkg_conf['packages']), shift=1)
    fm = FetcherManager(pkg_conf['repos'], paths)
    vers = {}
    for pkg in pkg_conf['packages']:
        pkg_name = pkg['name']
        pp.puts("%s" % pkg_name, shift=1)
        pkgd = {}
        vers[pkg_name] = pkgd
        for rls in pkg['releases']:
            pp.puts(rls['name'], shift=1)
            for repo in rls['repos']:
                repo_name = repo['repo']
                pp.puts(repo_name, shift=1)
                if not repo_name in pkgd:
                    pkgd[repo_name] = {}
                repod = pkgd[repo_name]
                for branch in repo['branches']:
                    if branch not in repod:
                        ver = fm.fetch_version(repo_name, pkg_name, branch)
                        repod[branch] = ver
                        ver_str = render_version(ver, show_error=True)
                        pp.puts("%s: %s" % (branch, ver_str))

                pp.shift(-1)
            pp.shift(-1)
        pp.shift(-1)
    pp.shift(-1)
    print
    return vers


def update_versions(pkg_conf, paths, ver_cache_fn):
    vers = fetch_versions(pkg_conf, paths)
    verwatch.util.mkdir_file(ver_cache_fn)
    json.dump(vers, open(ver_cache_fn, 'wb'))
    return vers


def cached_versions(ver_cache_fn):
    return json.load(open(ver_cache_fn, 'rb'))


def is_same_version(ver1, ver2):
    def _same_attr(h1, h2, attr):
        if attr in h1:
            if attr not in h2:
                return False
            return h1[attr] == h2[attr]
        else:
            return attr not in h2
    return _same_attr(ver1, ver2, 'version') and \
           _same_attr(ver1, ver2, 'release') and \
           _same_attr(ver1, ver2, 'epoch')


def render_version(ver, max_ver=None, show_error=False):
    s = ''
    if 'version' in ver:
        if 'epoch' in ver:
            e = ver['epoch']
            s += T.cyan(e) + T.bold_black(':')
        v = ver['version']
        if max_ver and v == max_ver:
            s += T.green(v)
        else:
            s += T.yellow(v)
        if 'release' in ver:
            r = ver['release']
            s += T.bold_black('-') + T.cyan(r)
    else:
        if show_error:
            try:
                err_msg = ver['error']
            except KeyError:
                err_msg = "BUG: No version fetched but fetcher didn't return error. Fetcher bug!"
        else:
            err_msg = '!!'
        s = T.red(err_msg)
    if 'next' in ver:
        next_ver = ver['next']
        if not is_same_version(ver, next_ver):
            s += ' -> ' + render_version(next_ver, max_ver)
    return s


def release_latest_version(rls, vers, pkg_name):
    max_verl = [0, 0, 0]
    for repo in rls['repos']:
        for branch in repo['branches']:
            try:
                ver = vers[pkg_name][repo['repo']][branch]
                while 'version' in ver:
                    v = ver['version']
                    verl = verwatch.util.ver2list(v)
                    max_verl = max(verl, max_verl)
                    if 'next_version' in ver:
                        ver = ver['next_version']
                    else:
                        ver = {}
            except KeyError:
                continue
    return '.'.join(map(str, max_verl))


def print_versions(pkg_conf, vers, package_filter=None, release_filter=None):
    pp = UberPrinter()
    first = True
    pkgs = pkg_conf['packages']
    if package_filter:
        pkgs = filter(lambda x: re.search(package_filter, x['name']), pkgs)
    for pkg in pkgs:
        rlss = pkg['releases']
        if release_filter:
            rlss = filter(lambda x: re.search(release_filter, x['name']), rlss)
            if not rlss:
                continue
        pkg_name = pkg['name']
        if first:
            first = False
        else:
            pp.puts("")
        pp.puts(T.bold("%s" % pkg_name), shift=1)
        for rls in rlss:
            pp.puts("[%s]" % T.bold(rls['name']), shift=1)
            max_ver = release_latest_version(rls, vers, pkg_name)
            # print all release versions
            for repo in rls['repos']:
                repo_name = repo['repo']
                pp.puts(T.bold(repo_name), shift=1)
                for branch in repo['branches']:
                    try:
                        ver = vers[pkg_name][repo_name][branch]
                        ver_str = render_version(ver, max_ver)
                    except KeyError:
                        ver_str = T.yellow('??')
                    pp.puts("%s: %s" % (branch, ver_str))
                pp.shift(-1)
            pp.shift(-1)
        pp.shift(-1)
    pp.shift(-1)
    return vers


