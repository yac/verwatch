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
            if 'options' in fch:
                options = fch['options']
            else:
                options = {}
            options['id'] = fch_name
            self.fchs[fch_name] = fcls(paths, options)

    def fetch_version(self, repo, pkg, branch):
        if repo not in self.fchs:
            raise ValueError("Repo '%s' not configured but referenced by '%s'." % (repo, pkg))
        return self.fchs[repo].get_version(pkg, branch)


class UberPrinter(object):
    def __init__(self, prefix='', indent_cols=2):
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
                        if 'version' in ver:
                            ver_str = ver['version']
                        else:
                            ver_str = ver
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


def render_version(ver, max_ver=None):
    s = ''
    if 'version' in ver:
        v = ver['version']
        if max_ver and v == max_ver:
            s = T.green(v)
        else:
            s = T.yellow(v)
        if 'release' in ver:
            r = ver['release']
            s += T.bold_black('-') + T.cyan(r)
    else:
        s = T.red('!!')
    if 'next' in ver:
        s += ' -> ' + render_version(ver['next'], max_ver)
    return s


def print_versions(pkg_conf, vers=None, rex_filter=None):
    if not vers:
        vers = cached_versions()
    pp = UberPrinter()
    for pkg in pkg_conf['packages']:
        pkg_name = pkg['name']
        if rex_filter and not re.search(rex_filter, pkg_name):
            continue
        pp.puts(T.bold("= %s =" % pkg_name), shift=1)
        for rls in pkg['releases']:
            pp.puts(T.bold(rls['name']), shift=1)
            # find latest version
            max_verl = [0, 0, 0]
            for repo in rls['repos']:
                for branch in repo['branches']:
                    try:
                        ver = vers[pkg_name][repo['repo']][branch]
                        v = ver['version']
                    except KeyError:
                        continue
                    verl = verwatch.util.ver2list(v)
                    max_verl = max(verl, max_verl)
            max_ver = '.'.join(map(str, max_verl))
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


