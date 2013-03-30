# -*- encoding: utf-8 -*-
import verwatch.core
import verwatch.conf

def help(paths):
    return """
Usage: verwatch [options] [PACKAGE_REGEX]

Show versions of packages matched by PACKAGE_REGEX.

Arguments:
  PACKAGE_REGEX   Regular expression to select packages.

Options:
  -p CONF --package-conf=CONF   Use package configuration file CONF. (default: %s)
  -u --update                   Update package version cache before listing version.
  -U --update-only              Update package version cache and exit.
  --version                     Print verwatch version and exit.
  -h --help                     Print this help and exit.

Paths:
  verwatch base:
  Package configs:
  Cache:
""" % verwatch.conf.DEFAULT_PKGCONF

from docopt import docopt


def main():
    paths = verwatch.conf.PathsManager()
    args = docopt(help(paths), version=verwatch.core.VERSION, help=True)

    if args['--package-conf']:
        pkg_conf_id = args['--package-conf']
    else:
        pkg_conf_id = None

    pkg_conf_fn = paths.get_package_conf_fn(pkg_conf_id)
    pkg_conf = verwatch.conf.get_package_conf(pkg_conf_fn)

    ver_cache_fn = paths.get_version_cache_fn(pkg_conf_id)

    if args['--update-only']:
        verwatch.core.update_versions(pkg_conf, paths, ver_cache_fn)
        return 0

    if args['--update']:
        vers = verwatch.core.update_versions(pkg_conf, paths, ver_cache_fn)
    else:
        try:
            vers = verwatch.core.cached_versions(ver_cache_fn)
        except IOError:
            print("Can't read cache file, fetching...")
            vers = verwatch.core.update_versions(pkg_conf, paths, ver_cache_fn)

    verwatch.core.print_versions(pkg_conf, vers)
    


if __name__ == '__main__':
    main()
