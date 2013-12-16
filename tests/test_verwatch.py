import verwatch.core
import verwatch.conf

import copy
import json
import os
import pytest
import shutil


BASE_DIR = 'tests/basedir'
TMP_DIR = 'tests/tmp'
CACHE_DIR = '%s/cache' % TMP_DIR

PATHS = verwatch.conf.PathsManager(base_dir=BASE_DIR, cache_dir=TMP_DIR)


def prep_dirs():
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)


def setup_module(module):
    prep_dirs()


@pytest.fixture
def pkg_conf():
    pkg_conf_fn = PATHS.get_package_conf_fn('base')
    pkg_conf_ = verwatch.conf.get_package_conf(pkg_conf_fn)
    return pkg_conf_


@pytest.fixture
def vers():
    vers_ = verwatch.core.fetch_versions(pkg_conf(), PATHS, vers={},
                                         quiet=True)
    return vers_


def test_update(vers):
    err_msg = vers['foo']['next']['v2']['error']
    assert vers['foo']['ver']['v1'] == {'version': '1.0'}
    ver_cnext = {'error': err_msg,
                 'next': {'version': '1.1'}}
    assert vers['foo']['next']['v2'] == ver_cnext
    ver_cboth = {'version': '1.0', 'next': {'version': '1.1'}}
    assert vers['bar']['both']['v1'] == ver_cboth
    assert vers['bar']['err']['v2'] == {'error': err_msg}


def test_diff_no_change(vers):
    old_vers = copy.deepcopy(vers)
    same_vers = copy.deepcopy(vers)
    vers_diff = verwatch.core.diff_versions(old_vers, same_vers)
    assert vers_diff == {}
    assert old_vers == vers
    assert same_vers == vers


def test_diff(vers):
    new_vers = copy.deepcopy(vers)
    err_msg = vers['foo']['next']['v2']['error']
    err_new = 'new error'
    # version change
    new_vers['foo']['ver']['v1']['version'] = '2.0'
    ver_ver = {'version': '2.0', 'was': {'version': '1.0'}}
    # next version chagne
    new_vers['foo']['next']['v2']['next']['version'] = '2.1'
    ver_next = {'error': err_msg, 'next': {'version': '2.1'},
                'was': {'error': err_msg, 'next': {'version': '1.1'}}}
    # version and next change
    new_vers['bar']['both']['v1']['version'] = '2.0'
    new_vers['bar']['both']['v1']['next']['version'] = '2.1'
    ver_both = {'version': '2.0', 'next': {'version': '2.1'}, 'was': {
        'version': '1.0', 'next': {'version': '1.1'}}}
    # error change
    new_vers['bar']['err']['v2']['error'] = err_new

    vers_diff = verwatch.core.diff_versions(vers, new_vers)
    # check individual changes first for easier debugging
    assert vers_diff['foo']['ver']['v1'] == ver_ver
    assert vers_diff['foo']['next']['v2'] == ver_next
    assert vers_diff['bar']['both']['v1'] == ver_both
    # error change doesn't matter
    assert 'err' not in vers_diff['bar'], "error change must not matter"
    # finally, check entire structure to prevent extras
    vers_good = {'foo': {'ver': {'v1': ver_ver}, 'next': {'v2': ver_next}},
                 'bar': {'both': {'v1': ver_both}}}
    assert vers_diff == vers_good, "there are extra items in the version diff"


def test_pkg_conf_filter_existing(pkg_conf, vers):
    new_vers = copy.deepcopy(vers)
    new_vers['bar']['next']['v2']['error'] = 'lolz'
    vers_diff = verwatch.core.diff_versions(vers, new_vers)
    filtered_pkg_conf = verwatch.core.filter_pkg_conf_existing_only(
        copy.deepcopy(pkg_conf), vers_diff)
    assert filtered_pkg_conf['packages'] == \
    [
        {
            "name": "bar",
            "releases": [
                {
                    "name": "release-banana",
                    "repos": [{"branches": ["v2"], "repo": "next"}]
                },
                {
                    "name": "release-grape",
                    "repos": [{"branches": ["v2"], "repo": "next" }]
                }
            ]
        }
    ]

