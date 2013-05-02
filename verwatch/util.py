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
