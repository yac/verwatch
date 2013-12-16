import copy
import os
import json
import glob
import imp


DEFAULT_PKGCONF = "default"


class PathsManager(object):
    def __init__(self, base_dir=None, cache_dir=None):
        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = "%s/.verwatch" % os.environ['HOME']
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            self.cache_dir = "%s/cache" % self.base_dir
        self.version_cache_dir = "%s/versions" % self.cache_dir
        self.pkgconf_dir = "%s/packages" % self.base_dir
        self.plugins_dir = "%s/plugins" % self.base_dir

    def get_package_conf_fn(self, conf=None):
        if not conf:
            conf = DEFAULT_PKGCONF
        return "%s/%s.json" % (self.pkgconf_dir, conf)

    def get_version_cache_fn(self, conf=None):
        if not conf:
            conf = DEFAULT_PKGCONF
        return "%s/%s.json" % (self.version_cache_dir, conf)


def get_package_conf(conf_fn):
    pkg_conf = json.load(open(conf_fn))
    pkgs = pkg_conf['packages']
    # expand multiple packages
    for i, pkg in enumerate(pkgs):
        if 'names' not in pkg:
            continue
        pkgs.remove(pkg)
        names = pkg.pop('names')
        for name in reversed(names):
            npkg = copy.deepcopy(pkg)
            npkg['name'] = name
            pkgs.insert(i, npkg)
    return pkg_conf



def import_file(fn):
    (path, name) = os.path.split(fn)
    (name, ext) = os.path.splitext(name)

    (file, filename, data) = imp.find_module(name, [path])
    return imp.load_module(name, file, filename, data)


def import_files(path):
    """
    Import all *.py files in specified directory.
    """
    n = 0
    for pyfile in glob.glob('%s/*.py' % path):
        import_file(pyfile)
        n += 1
    return n
