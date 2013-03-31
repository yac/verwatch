import subprocess
import os
import re


def is_version(ver):
    return re.match('v?[0-9]', ver) is not None


def vr(nvr, name):
    if nvr.startswith(name):
        vr = nvr[len(name)+1:]
        # TODO: might contain more than one '-'
        return vr.split('-')
    return nvr, ''


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
    return (errcode, out, err)


def mkdir_file(file_path):
    dir_path = os.path.dirname(file_path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
