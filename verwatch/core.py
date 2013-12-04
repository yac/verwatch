# -*- encoding: utf-8 -*-

import util
import fetch

import re
import json
import blessings


VERSION = '0.4'

TERM = blessings.Terminal()
TERM_PLAIN = util.PlainTerminal()


def _get_term(color):
    if color:
        return TERM
    return TERM_PLAIN


class FetcherManager(object):
    def __init__(self, repo_conf, paths):
        self.fchs = {}
        for fch_name, fch in repo_conf.items():
            fch_cls = fch['fetcher']
            if fch_cls not in fetch.VersionFetcher.fetchers:
                raise NotImplementedError(
                    "Version fetcher '%s' is not available." % fch_cls)
            fcls = fetch.VersionFetcher.fetchers[fch_cls]
            options = fch.get('options', {})
            options['id'] = fch_name
            self.fchs[fch_name] = fcls(paths=paths,
                                       options=options,
                                       alter_pkg_name=fch.get('alter_pkg_name'))

    def fetch_version(self, repo, pkg, branch):
        if repo not in self.fchs:
            raise ValueError("Repo '%s' not configured but referenced by '%s'."
                             % (repo, pkg))
        return self.fchs[repo].get_version(pkg, branch)


class UberPrinter(object):
    def __init__(self, prefix='', indent_cols=4, string_output=False):
        self.prefix = prefix
        self.indent_cols = indent_cols
        self.indent = 0
        self.indent_str = ''
        self.s = ''
        self.string_output = string_output

    def shift(self, n):
        self.indent += n
        self.indent_str = self.indent * self.indent_cols * ' '

    def puts(self, pstr="", shift=0):
        s = "%s%s%s" % (self.prefix, self.indent_str, str(pstr))
        if self.string_output:
            self.s += s + '\n'
        else:
            print(s)
        if shift:
            self.shift(shift)


def repo_tags(repo, pkg_conf):
    local_tags = set(repo.get('tags', []))
    repos = pkg_conf['repos']
    global_tags = set(repos.get(repo.get('repo'), {}).get('tags', []))
    tags = local_tags.union(global_tags)
    return tags


def filter_pkg_conf(pkg_conf, package_filter=None, release_filter=None,
                    repo_tag_filter=None):
    pkgs = pkg_conf['packages']
    if package_filter:
        pkgs = filter(lambda x: re.search(package_filter, x['name']), pkgs)
    if release_filter:
        for pkg in pkgs:
            pkg['releases'] = \
                filter(lambda x: re.search(release_filter, x['name']),
                       pkg['releases'])
        pkgs = [e for e in pkgs if e['releases']]
    if repo_tag_filter:
        def _match_tag_filter(repo):
            tags = repo_tags(repo, pkg_conf)
            if not tags:
                return False
            for ftag in repo_tag_filter:
                for tag in tags:
                    if tag == ftag:
                        return True
            return False
        for pkg in pkgs:
            rlss = pkg['releases']
            for rls in rlss:
                rls['repos'] = filter(_match_tag_filter, rls['repos'])
            pkg['releases'] = [e for e in rlss if e['repos']]
        pkgs = [e for e in pkgs if e['releases']]
    pkg_conf['packages'] = pkgs
    return pkg_conf


def filter_pkg_conf_existing_only(pkg_conf, vers):
    pkgs = pkg_conf['packages']
    for pkg in pkgs:
        pkg_name = pkg['name']
        rlss = pkg['releases']
        for rls in rlss:
            repos = rls['repos']
            for repo in repos:
                repo_name = repo['repo']

                def _version_available(branch):
                    # one-liner using try..except is too slow for this :(
                    if pkg_name not in vers:
                        return False
                    pkg_ = vers[pkg_name]
                    if repo_name not in pkg_:
                        return False
                    repo_ = pkg_[repo_name]
                    if branch not in repo_:
                        return False
                    ver_ = repo_[branch]
                    if not ('version' in ver_ or 'next' in ver_):
                        return False
                    return True

                repo['branches'] = filter(_version_available, repo['branches'])
            rls['repos'] = [e for e in repos if e['branches']]
        pkg['releases'] = [e for e in rlss if e['repos']]
    pkgs = [e for e in pkgs if e['releases']]
    pkg_conf['packages'] = pkgs
    return pkg_conf


def fetch_versions(pkg_conf, paths, vers=None, show_commands=False, color=True):
    t = _get_term(color)
    if not vers:
        vers = {}
    pp = UberPrinter(prefix=t.yellow('[fetch] '))
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
                repo_title = util.get_repo_title(pkg_conf, repo_name)
                pp.puts(repo_title, shift=1)
                if not repo_name in pkgd:
                    pkgd[repo_name] = {}
                repod = pkgd[repo_name]
                for branch in repo['branches']:
                    ver = fm.fetch_version(repo_name, pkg_name, branch)
                    if show_commands and 'cmd' in ver:
                        pp.puts('$ %s' % ver['cmd'])
                    repod[branch] = ver
                    ver_str = render_version(ver, show_error=True, color=color)
                    pp.puts("%s: %s" % (branch, ver_str))
                pp.shift(-1)
            pp.shift(-1)
        pp.shift(-1)
    pp.shift(-1)
    pp.puts()
    return vers


def update_versions(pkg_conf, paths, ver_cache_fn, vers=None,
                    show_commands=False, color=True):
    vers = fetch_versions(pkg_conf, paths, vers, show_commands=show_commands,
                          color=color)
    util.mkdir_file(ver_cache_fn)
    json.dump(vers, open(ver_cache_fn, 'wb'))
    return vers


def cached_versions(ver_cache_fn):
    return json.load(open(ver_cache_fn, 'rb'))


def render_version(ver, max_ver=None, show_error=False, color=True):
    t = _get_term(color)
    s = ''
    if 'version' in ver:
        if 'epoch' in ver:
            e = str(ver['epoch'])
            s += t.cyan(e) + t.bold_black(':')
        v = ver['version']
        if max_ver and v == max_ver:
            s += t.green(v)
        else:
            s += t.yellow(v)
        if 'release' in ver:
            r = ver['release']
            s += t.bold_black('-') + t.cyan(r)
    else:
        if show_error:
            try:
                err_msg = ver['error']
            except KeyError:
                err_msg = ("BUG: No version fetched but fetcher didn't return "
                           "error. Fetcher bug!")
        else:
            err_msg = '!!'
        s = t.red(err_msg)
    if 'next' in ver:
        next_ver = ver['next']
        if not util.is_same_version(ver, next_ver):
            s += ' -> ' + render_version(next_ver, max_ver=max_ver, color=color)
    if 'was' in ver:
        was_ver = ver['was']
        s += '  (was: %s)' % render_version(was_ver, max_ver=max_ver,
                                            color=color)
    return s


def print_versions(pkg_conf, vers, show_commands=False, color=True,
                   string_output=False):
    t = _get_term(color)
    pp = UberPrinter(string_output=string_output)
    first = True
    pkgs = pkg_conf['packages']
    for pkg in pkgs:
        rlss = pkg['releases']
        pkg_name = pkg['name']
        if first:
            first = False
        else:
            pp.puts("")
        pp.puts(t.bold("%s" % pkg_name), shift=1)
        for rls in rlss:
            pp.puts("[%s]" % t.bold(rls['name']), shift=1)
            max_ver = util.release_latest_version(rls, vers, pkg_name)
            # print all release versions
            for repo in rls['repos']:
                repo_name = repo['repo']
                repo_title = util.get_repo_title(pkg_conf, repo_name)
                pp.puts(t.bold(repo_title), shift=1)
                for branch in repo['branches']:
                    try:
                        ver = vers[pkg_name][repo_name][branch]
                        ver_str = render_version(ver,
                                                 color=color, max_ver=max_ver)
                    except KeyError:
                        ver_str = t.yellow('??')
                    if show_commands and 'cmd' in ver:
                        pp.puts("$ %s" % ver['cmd'])
                    pp.puts("%s: %s" % (branch, ver_str))
                pp.shift(-1)
            pp.shift(-1)
        pp.shift(-1)
    pp.shift(-1)
    if string_output:
        return pp.s


def dget(d, key):
    # I don't know howto make nested defaultdict, thus this uglyness
    if key not in d:
        d[key] = {}
    return d[key]


def _insert_new_version(diff, pkg_name, repo_name, branch_name, new_version,
                        old_version):
    repo = dget(dget(diff, pkg_name), repo_name)
    diff_version = new_version.copy()
    if old_version:
        diff_version['was'] = old_version
    repo[branch_name] = diff_version


def diff_versions(old_vers, new_vers):
    diff = {}
    for pkg_name, new_repos in new_vers.items():
        old_repos = old_vers.get(pkg_name, {})
        for repo_name, new_branches in new_repos.items():
            old_branches = old_repos.get(repo_name, {})
            for branch_name, new_version in new_branches.items():
                old_version = old_branches.get(branch_name, {})
                if new_version != old_version:
                    _insert_new_version(diff, pkg_name, repo_name,
                                        branch_name, new_version, old_version)
    return diff
