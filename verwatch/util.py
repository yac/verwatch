import subprocess
import os
import re


def is_version(ver):
    return re.match('v?[0-9]', ver) is not None


def parse_nvr(nvr, name):
    if nvr.startswith(name):
        vr = nvr[len(name) + 1:]
        # TODO: might contain more than one '-'
        ri = vr.rfind('-')
        if ri < 0:
            return {'version': vr}
        ver = {}
        v = vr[0:ri]
        ver['release'] = vr[ri + 1:]
        ei = v.find(':')
        if ei >= 0:
            ver['epoch'] = v[0:ei]
            ver['version'] = v[ei + 1:]
        else:
            ver['version'] = v
        return ver
    return {'error': 'Unable to parse version: %s' % nvr}


def ver2list(ver):
    def _int(s):
        try:
            return int(s)
        except ValueError:
            return s
    verl = ver.split('.')
    return map(_int, verl)


def get_repo_title(pkg_conf, repo):
    return pkg_conf["repos"][repo].get("title", repo)


def release_latest_version(rls, vers, pkg_name):
    max_verl = [0, 0, 0]
    for repo in rls['repos']:
        for branch in repo['branches']:
            try:
                ver = vers[pkg_name][repo['repo']][branch]
                while 'version' in ver:
                    v = ver['version']
                    verl = ver2list(v)
                    max_verl = max(verl, max_verl)
                    if 'next_version' in ver:
                        ver = ver['next_version']
                    else:
                        ver = {}
            except KeyError:
                continue
    return '.'.join(map(str, max_verl))


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


def run(cmd):
    prc = subprocess.Popen(cmd, shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    out, err = prc.communicate()
    errcode = prc.returncode
    return (errcode, out.rstrip(), err.rstrip())


def mkdir_file(file_path):
    dir_path = os.path.dirname(file_path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
