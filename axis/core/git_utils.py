"""git_utils.py: Django core"""

import codecs
import collections
import datetime
import logging
import re
import subprocess
from configparser import ConfigParser

from dateutil.tz import os, tzoffset
from django.apps import apps

__author__ = "Steven Klass"
__date__ = "11/16/14 8:05 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

tzaz = tzoffset("America/Phoenix", -7 * 60 * 60)


def _convert_to_local(dt, local_timezone):
    local_time = (dt + local_timezone.utcoffset(None)).replace(tzinfo=local_timezone)
    return local_time.strftime("%a, %-d %b %Y %H:%M:%S %Z")


def _parse_timestamp(date_string):
    """Allow you parse most basic timestamps with TZ Info"""
    date_string_elements = [date_string]
    tz = None
    if date_string[-5] in ["-", "+"]:
        date_string_elements = [date_string[:-5], date_string[-5:]]
        label = None
        if date_string_elements[1].replace(":", "") == "-0700":
            label = "America/Phoenix"
        elif date_string_elements[1].replace(":", "") == "+0000":
            label = "UTC"
        neg, hours, minutes = (
            date_string_elements[1][0],
            int(date_string_elements[1][1:3]),
            int(date_string_elements[1][-2:]),
        )
        neg = 1 if neg == "+" else -1
        tz = tzoffset(label, neg * (hours * 60 * 60 + minutes * 60))
    date_string_short = date_string_elements[0]

    date_object = datetime.datetime.strptime(date_string_short, "%Y-%m-%d %H:%M:%S.%f")

    if tz:
        date_object = date_object.replace(tzinfo=tz)
    return date_object


GitStatus = collections.namedtuple(
    "GitStatus", "path sha date author description branch url href version".split()
)


def get_git_version_info(path, base_url="https://github.com/pivotal-energy-solutions/axis"):
    """Get the version based on a path"""

    from django.conf import settings

    os.chdir(os.path.abspath(settings.SITE_ROOT))
    assert os.path.join(os.path.abspath(settings.SITE_ROOT), path)

    cmd = ["git", "log", "-1", "--pretty=format:%h|%ad|%an|%d|%s", "--date=raw", "--", path]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")
    sha, _date, author, _branch, description = stdout.split("\n")[0].split("|")
    cmd = ["git", "describe", "--tags", sha]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")
    version = [line.strip() for line in stdout.split("\n")][0]
    cmd = ["git", "branch"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")
    branch = [line.split("*")[1].strip() for line in stdout.split("\n") if line.startswith("*")][0]

    if "(" in _branch or "Tag" in _branch:
        try:
            branch = re.search(r"[\(|\s]origin/(.*)[\)|,]", _branch).group(1).split(" ")[0]
            branch = branch[:-1] if branch.endswith(",") else branch
        except AttributeError:
            pass

    if os.path.isdir(path):
        # https://github.com/pivotal-energy-solutions/axis/tree/master/apps/aws
        url = "{}/tree/{}{}".format(
            base_url, branch if branch.endswith("/") else branch + "/", path if path != "." else ""
        )
    else:
        # https://github.com/pivotal-energy-solutions/axis/blob/master/.gitmodules

        url = "{}/blob/{}/{}".format(base_url, branch, path)
        if len(branch) and "(" not in branch:
            # https://github.com/pivotal-energy-solutions/axis/blob/e0b927c62/apps/checklist/homechecklist_views.py
            # url = "{}/blob/{}/{}".format(base_url, sha, path)
            # https://github.com/pivotal-energy-solutions/axis/commit/e0b927c6293b
            url = "{}/commit/{}".format(base_url, sha, path)

    _date = (
        datetime.datetime.fromtimestamp(float(_date.split()[0])).strftime("%Y-%m-%d %H:%M:%S.%f")
        + _date.split()[1]
    )
    date = _convert_to_local(_parse_timestamp(_date), tzaz)

    href = '<a href="{url}" style="#ccc">{sha}</a> [{author}] {date} {description}'.format(
        url=url, sha=sha, author=author, date=date, description=re.sub(r"%", "", description)
    )

    return GitStatus(path, sha, date, author, description, branch, url, href, version)


def set_version_numbers(filename=None):
    """This will set all axis version numbers use this as the app deploys"""

    def set_config_version_info(config, section, path):
        try:
            version_info = get_git_version_info(path)
        except ValueError:
            log.warning("Skipping %s - %s", section, path)
            return config

        log.debug("Setting %s to %s", section, version_info.version)
        config.add_section(section)
        config.set(section, "path", path)
        config.set(section, "version", version_info.version)
        config.set(section, "last_update", version_info.date)
        config.set(section, "author", version_info.author)
        config.set(section, "branch", version_info.branch)
        config.set(section, "sha", version_info.sha)
        config.set(section, "url", version_info.url)
        config.set(section, "href", version_info.href)
        config.set(section, "description", re.sub(r"%", "pct", version_info.description))
        return config

    config = ConfigParser()
    axis_base_path = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
    set_config_version_info(config, "base", axis_base_path)

    for app_label, app_config in apps.app_configs.items():
        if not os.path.isdir(os.path.join(axis_base_path, app_config.path)):
            log.debug(
                "Skipping %s - it's ok it's not in our path %s", app_config.path, axis_base_path
            )
            continue
        set_config_version_info(config, app_label, app_config.path)

    set_config_version_info(config, "aws", os.path.join(axis_base_path, "axis", "aws"))
    set_config_version_info(
        config, "better_generics", os.path.join(axis_base_path, "axis", "better_generics")
    )

    filename = filename if filename else os.path.join(axis_base_path, "._versions")
    with codecs.open(filename, encoding="utf-8", mode="wb") as cfg:
        config.write(cfg)


def get_config_file_version_info(app, full=False, versions_file="._versions"):
    """Get the stored version from a file - Do NOT pull in django for this"""
    try:
        with codecs.open(versions_file, encoding="utf-8") as fp:
            config = ConfigParser()
            config.read_file(fp)
            try:
                if full:
                    return GitStatus(
                        config.get(app, "path"),
                        config.get(app, "sha"),
                        config.get(app, "last_update"),
                        config.get(app, "author"),
                        config.get(app, "description"),
                        config.get(app, "branch"),
                        config.get(app, "url"),
                        config.get(app, "href"),
                        config.get(app, "version"),
                    )
                return tuple(config.get(app, "version").split("."))
            except Exception as err:
                log.error("Unable to read git status from file %s - %s", versions_file, err)
                if full:
                    return GitStatus(app, "", "", "", "", "", "", "", "1-0-not_listed")
                return 1, 0, "not_listed"
    except:
        if full:
            return GitStatus(app, "", "", "", "", "", "", "", "1-0-unknown")
        return 1, 0, "unknown"


def get_stored_version_info(app, full=True, versions_file="._versions"):
    return get_config_file_version_info(app, full, versions_file)
