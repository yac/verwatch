# -*- encoding: utf-8 -*-
import verwatch.core
import verwatch.conf
import verwatch.fetch
import verwatch.html
import os.path


def help(paths):
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
  -u --update                   Update package version cache before listing
                                versions.
  -U --update-only              Update package version cache and exit.
  -c --show-commands            Show commands used to obtain versions.
  -H --html                     Output standalone styled HTML page.
  --html-embed                  Output raw embeddable HTML.
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
          'pkgconf': verwatch.conf.DEFAULT_PKGCONF,
          'pkgconf_fn': paths.get_package_conf_fn('CONF'),
          'base_dir': paths.base_dir,
          'pkgconf_dir': paths.pkgconf_dir,
          'plugins_dir': paths.plugins_dir,
          'cache_dir': paths.cache_dir,
          'fetchers': "\n  ".join(sorted(
                                verwatch.fetch.VersionFetcher.fetchers.keys()))
      }

from docopt import docopt


def main():
    paths = verwatch.conf.PathsManager()
    # import user plugins
    verwatch.conf.import_files(paths.plugins_dir)

    args = docopt(help(paths), version=verwatch.core.VERSION, help=True)

    show_cmd = args['--show-commands']
    update = args['--update'] or args['--update-only']
    if args['--package-conf']:
        pkg_conf_id = args['--package-conf']
    else:
        pkg_conf_id = None

    # get and filter package configuration
    pkg_conf_fn = paths.get_package_conf_fn(pkg_conf_id)
    pkg_conf = verwatch.conf.get_package_conf(pkg_conf_fn)
    pkg_conf = verwatch.core.filter_pkg_conf(pkg_conf, args['PACKAGE_REGEX'],
                                             args['--release'])

    ver_cache_fn = paths.get_version_cache_fn(pkg_conf_id)

    if os.path.isfile(ver_cache_fn):
        vers = verwatch.core.cached_versions(ver_cache_fn)
    else:
        vers = {}
        update = True
        print "No version cache, updating."

    if update:
        vers = verwatch.core.update_versions(pkg_conf, paths, ver_cache_fn,
                                             vers, show_cmd)
        if args['--update-only']:
            return 0

    if args['--html']:
        print verwatch.html.render_versions_html_page(pkg_conf, vers)
    elif args['--html-embed']:
        print verwatch.html.render_versions_html(pkg_conf, vers)
    else:
        verwatch.core.print_versions(pkg_conf, vers, show_cmd)


if __name__ == '__main__':
    main()
