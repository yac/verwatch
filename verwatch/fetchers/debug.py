from verwatch.fetch import VersionFetcher
from verwatch.util import run, parse_nvr

import os
import re


class DebugFetcher(VersionFetcher):
    name = 'debug'

    def __init__(self, **kwargs):
        super(DebugFetcher, self).__init__(**kwargs)
        if 'paths' not in kwargs:
            raise ValueError("paths argument not supplied to debug "
                             "fetcher.")
        options = kwargs.get('options', {})
        self.paths = kwargs['paths']
        self.version = options.get('version')
        self.error = options.get('error', 'version not set')
        self.next = options.get('next')
        # bumping
        self.bump_version_path = None
        self.bump_next_path = None
        self.bump_dir = None
        bump = options.get('bump')
        if bump:
            self.bump_dir = "%s/%s" % (self.paths.cache_dir, self.name)
            if not os.path.isdir(self.bump_dir):
                os.makedirs(self.bump_dir)
            if bump == 'version' or bump == 'both':
                self.bump_version_path = "%s/%s.version" % (self.bump_dir,
                                                            options['id'])
            if bump == 'next' or bump == 'both':
                self.bump_next_path = "%s/%s.next" % (self.bump_dir,
                                                      options['id'])

    def _bump_version(self, ver, bump_file_path):
        if not ver or not bump_file_path:
            return ver
        try:
            f = open(bump_file_path, 'r')
            ver = f.read().strip()
            f.close()
        except Exception as ex:
            print("[debug] Can't read bump info: %s" % bump_file_path)
            print(str(ex))
            pass
        ver_list = ver.split('.')
        new_ver = ver
        try:
            ver_list[-1] = str(int(ver_list[-1]) + 1)
            new_ver = ".".join(ver_list)
            try:
                f = open(bump_file_path, 'w')
                f.write(new_ver)
            except Exception as ex:
                print("[debug] Can't save bump info: %s" % bump_file_path)
                pass
        except ValueError:
            print("[debug] failed to bump version: %s" % ver)
        return new_ver

    def _get_version(self, pkg_name, branch):
        ver = {}
        if self.version:
            self.version = self._bump_version(self.version,
                                              self.bump_version_path)
            ver['version'] = self.version
        else:
            ver['error'] = self.error
        if self.next:
            self.next = self._bump_version(self.next, self.bump_next_path)
            ver['next'] = {'version': self.next}
        return ver
