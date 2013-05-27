# -*- encoding: utf-8 -*-

import verwatch.conf
import verwatch.util
import verwatch.builtin_fetchers
import verwatch.fetch

import os
import re
import json
import blessings


VERSION = '0.2'
T = blessings.Terminal()


class FetcherManager(object):
    def __init__(self, repo_conf, paths):
        self.fchs = {}
        for fch_name, fch in repo_conf.items():
            fch_cls = fch['fetcher']
            if fch_cls not in verwatch.fetch.VersionFetcher.fetchers:
                raise NotImplementedError(
                            "Version fetcher '%s' is not available." % fch_cls)
            fcls = verwatch.fetch.VersionFetcher.fetchers[fch_cls]
            options = fch.get('options', {})
            options['id'] = fch_name
            self.fchs[fch_name] = fcls(paths=paths,
                                       options=options,
                                       alter_pkg_name=fch.get('alter_pkg_name')
                                       )

    def fetch_version(self, repo, pkg, branch):
        if repo not in self.fchs:
            raise ValueError("Repo '%s' not configured but referenced by '%s'."
                             % (repo, pkg))
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

    def puts(self, pstr="", shift=0):
        print "%s%s%s" % (self.prefix, self.indent_str, str(pstr))
        if shift:
            self.shift(shift)


def filter_pkg_conf(pkg_conf, package_filter=None, release_filter=None):
    pkgs = pkg_conf['packages']
    if package_filter:
        pkgs = filter(lambda x: re.search(package_filter, x['name']), pkgs)
    if release_filter:
        for pkg in pkgs:
            rlss = filter(lambda x: re.search(release_filter, x['name']),
                          pkg['releases'])
            if not rlss:
                pkgs.remove(pkg)
            else:
                pkg['releases'] = rlss
    pkg_conf['packages'] = pkgs
    return pkg_conf


def fetch_versions(pkg_conf, paths, vers={}, show_commands=False):
    pp = UberPrinter(T.yellow('[fetch] '))
    pp.puts("Fetching versions of %s packages:" % len(pkg_conf['packages']),
            shift=1)
    fm = FetcherManager(pkg_conf['repos'], paths)
    for pkg in pkg_conf['packages']:
        pkg_name = pkg['name']
        pp.puts("%s" % pkg_name, shift=1)
        if pkg_name not in vers:
            vers[pkg_name] = {}
        pkgd = vers[pkg_name]
        for rls in pkg['releases']:
            pp.puts(rls['name'], shift=1)
            for repo in rls['repos']:
                repo_name = repo['repo']
                repo_title = verwatch.util.get_repo_title(pkg_conf, repo_name)
                pp.puts(repo_title, shift=1)
                if not repo_name in pkgd:
                    pkgd[repo_name] = {}
                repod = pkgd[repo_name]
                for branch in repo['branches']:
                    ver = fm.fetch_version(repo_name, pkg_name, branch)
                    if show_commands and 'cmd' in ver:
                        pp.puts('$ %s' % ver['cmd'])
                    repod[branch] = ver
                    ver_str = render_version(ver, show_error=True)
                    pp.puts("%s: %s" % (branch, ver_str))
                pp.shift(-1)
            pp.shift(-1)
        pp.shift(-1)
    pp.shift(-1)
    pp.puts()
    return vers


def update_versions(pkg_conf, paths, ver_cache_fn, vers={}, show_cmd=False):
    vers = fetch_versions(pkg_conf, paths, vers, show_cmd)
    verwatch.util.mkdir_file(ver_cache_fn)
    json.dump(vers, open(ver_cache_fn, 'wb'))
    return vers


def cached_versions(ver_cache_fn):
    return json.load(open(ver_cache_fn, 'rb'))


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
                err_msg = ("BUG: No version fetched but fetcher didn't return "
                           "error. Fetcher bug!")
        else:
            err_msg = '!!'
        s = T.red(err_msg)
    if 'next' in ver:
        next_ver = ver['next']
        if not verwatch.util.is_same_version(ver, next_ver):
            s += ' -> ' + render_version(next_ver, max_ver)
    return s


def print_versions(pkg_conf, vers, show_commands=False):
    pp = UberPrinter()
    first = True
    pkgs = pkg_conf['packages']
    for pkg in pkgs:
        rlss = pkg['releases']
        pkg_name = pkg['name']
        if first:
            first = False
        else:
            pp.puts("")
        pp.puts(T.bold("%s" % pkg_name), shift=1)
        for rls in rlss:
            pp.puts("[%s]" % T.bold(rls['name']), shift=1)
            max_ver = verwatch.util.release_latest_version(rls, vers, pkg_name)
            # print all release versions
            for repo in rls['repos']:
                repo_name = repo['repo']
                repo_title = verwatch.util.get_repo_title(pkg_conf, repo_name)
                pp.puts(T.bold(repo_title), shift=1)
                for branch in repo['branches']:
                    try:
                        ver = vers[pkg_name][repo_name][branch]
                        ver_str = render_version(ver, max_ver)
                    except KeyError:
                        ver_str = T.yellow('??')
                    if show_commands and 'cmd' in ver:
                        pp.puts("$ %s" % ver['cmd'])
                    pp.puts("%s: %s" % (branch, ver_str))
                pp.shift(-1)
            pp.shift(-1)
        pp.shift(-1)
    pp.shift(-1)
    return vers
