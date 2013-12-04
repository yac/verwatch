# -*- encoding: utf-8 -*-
import core
import conf
import copy
import fetch
import html


from docopt import docopt
import os.path


def get_help(paths):
    return """
Usage: verwatch [options] [PACKAGE_REGEX]

Show versions of packages matched by PACKAGE_REGEX.

Arguments:
  PACKAGE_REGEX   Only packages matching this regular expression will be
                  listed/updated.

Options:
  -p CONF --package-conf=CONF   Use package configuration file CONF.
                                Default: "%(pkgconf)s"
                                Maps to: %(pkgconf_fn)s
  -r REGEX --release=REGEX      Only releases matching regular expression REGEX
                                will be listed/updated.
  -u --update                   Update version cache before listing versions.
  -U --update-only              Update version cache and exit.
  -d --update-diff              Update version cache and print version changes.
  -c --show-commands            Show commands used to obtain versions.
  -H --html                     Output standalone styled HTML page.
  --html-embed                  Output raw embeddable HTML.
  --no-color                    Don't use colors in terminal output.
  --version                     Print verwatch version and exit.
  -h --help                     Print this help and exit.

Paths:
  verwatch base      %(base_dir)s
  package configs    %(pkgconf_dir)s
  plugins            %(plugins_dir)s
  cache              %(cache_dir)s

Available version fetchers:
  %(fetchers)s
""" % {
        'pkgconf': conf.DEFAULT_PKGCONF,
        'pkgconf_fn': paths.get_package_conf_fn('CONF'),
        'base_dir': paths.base_dir,
        'pkgconf_dir': paths.pkgconf_dir,
        'plugins_dir': paths.plugins_dir,
        'cache_dir': paths.cache_dir,
        'fetchers': "\n  ".join(sorted(
            fetch.VersionFetcher.fetchers.keys()))
    }


def main():
    paths = conf.PathsManager()
    # import user plugins
    conf.import_files(paths.plugins_dir)

    args = docopt(get_help(paths), version=core.VERSION, help=True)

    show_cmd = args['--show-commands']
    color = not args['--no-color']
    update = args['--update'] or args['--update-only'] or args['--update-diff']
    update_diff = args['--update-diff']
    if args['--package-conf']:
        pkg_conf_id = args['--package-conf']
    else:
        pkg_conf_id = None

    # get and filter package configuration
    pkg_conf_fn = paths.get_package_conf_fn(pkg_conf_id)
    pkg_conf = conf.get_package_conf(pkg_conf_fn)
    pkg_conf = core.filter_pkg_conf(pkg_conf, args['PACKAGE_REGEX'],
                                    args['--release'])

    ver_cache_fn = paths.get_version_cache_fn(pkg_conf_id)

    if os.path.isfile(ver_cache_fn):
        vers = core.cached_versions(ver_cache_fn)
    else:
        vers = {}
        update = True
        print "No version cache, updating."

    if update:
        if update_diff:
            old_vers = copy.deepcopy(vers)
        vers = core.update_versions(pkg_conf, paths, ver_cache_fn, vers,
                                    show_commands=show_cmd, color=color)
        if args['--update-only']:
            return 0
        if update_diff:
            vers = core.diff_versions(old_vers, vers)
            pkg_conf = core.filter_pkg_conf_existing_only(pkg_conf, vers)

    if args['--html']:
        print html.render_versions_html_page(pkg_conf, vers)
    elif args['--html-embed']:
        print html.render_versions_html(pkg_conf, vers)
    else:
        core.print_versions(pkg_conf, vers, show_commands=show_cmd, color=color)


if __name__ == '__main__':
    main()
