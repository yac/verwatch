import os
import json

DEFAULT_PKGCONF = "default"


class PathsManager(object):
    def __init__(self, base_dir=None):
        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = "%s/.verwatch" % os.environ['HOME']
        self.pkgconf_dir = "%s/packages" % self.base_dir
        self.cache_dir = "%s/cache" % self.base_dir
        self.version_cache_dir = "%s/versions" % self.cache_dir

    def get_package_conf_fn(self, conf=None):
        if not conf:
            conf = DEFAULT_PKGCONF
        return "%s/%s.json" % (self.pkgconf_dir, conf)

    def get_version_cache_fn(self, conf=None):
        if not conf:
            conf = DEFAULT_PKGCONF
        return "%s/%s.json" % (self.version_cache_dir, conf)


def get_package_conf(conf_fn):
    return json.load(open(conf_fn))
