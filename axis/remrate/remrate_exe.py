"""remrate.py: Django remrate"""


import collections
import datetime
import logging
import os
import pprint
import re
import sys
import time

import dateutil.parser

__author__ = "Steven Klass"
__date__ = "8/27/14 10:45 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

if hasattr(sys, "getwindowsversion"):
    try:
        import psutil
        import pywinauto
        from pywinauto import application, findwindows, MatchError
        from pywinauto.timings import WaitUntilPasses
    except ImportError:
        pass
else:
    Warning("This is a WINDOWS tool - You've been warned")

VersionData = collections.namedtuple(
    "REMRateExeDetails", ["exe_path", "title_regex", "description", "version"]
)
VersionInfo = collections.namedtuple("Version", ["label", "major", "minor", "patch", "flavor"])

VERSIONS = collections.OrderedDict(
    [
        (
            "r1461",
            VersionData(
                "C:\\Program Files\\Architectural Energy Corporation\\REM Rate 14.6.1\\REMRate14.exe",
                "REM/Rate v 14.6.1   - {blg_file}",
                "REM/Rate v 14.6.1",
                VersionInfo("14.6.1", 14, 6, 1, "rate"),
            ),
        ),
        (
            "r146",
            VersionData(
                "C:\\Program Files\\Architectural Energy Corporation\\REM Rate 14.6\\REMRate14.exe",
                "REM/Rate v 14.6   - {blg_file}",
                "REM/Rate v 14.6",
                VersionInfo("14.6", 14, 6, 0, "rate"),
            ),
        ),
        (
            "r1451",
            VersionData(
                "C:\\Program Files\\Architectural Energy Corporation\\REM Rate 14.5.1\\REMRate14.exe",
                "REM/Rate v 14.5.1   - {blg_file}",
                "REM/Rate v 14.5.1",
                VersionInfo("14.5.1", 14, 5, 1, "rate"),
            ),
        ),
        (
            "r145",
            VersionData(
                "C:\\Program Files\\Architectural Energy Corporation\\REM Rate 14.5\\REMRate14.exe",
                "REM/Rate v 14.5   - {blg_file}",
                "REM/Rate v 14.5",
                VersionInfo("14.5", 14, 5, 0, "rate"),
            ),
        ),
        (
            "r1441",
            VersionData(
                "C:\\Program Files\\Architectural Energy Corporation\\REM Rate 14.4.1\\REMRate14.exe",
                "REM/Rate v 14.4.1  - {blg_file}",
                "REM/Rate v 14.4.1",
                VersionInfo("14.4.1", 14, 4, 1, "rate"),
            ),
        ),
        (
            "r144",
            VersionData(
                "C:\\Program Files\\Architectural Energy Corporation\\REM Rate 14.4\\REMRate14.exe",
                "REM/Rate v 14.4  - {blg_file}",
                "REM/Rate v 14.4",
                VersionInfo("14.4", 14, 4, 0, "rate"),
            ),
        ),
        (
            "r143",
            VersionData(
                "C:\\Program Files\\Architectural Energy Corporation\\REM Rate 14.3\\REMRate14.exe",
                "REM/Rate v 14.3  - {blg_file}",
                "REM/Rate v 14.3",
                VersionInfo("14.3", 14, 3, 0, "rate"),
            ),
        ),
        (
            "r142",
            VersionData(
                "C:\\Program Files\\Architectural Energy Corporation\\REM Rate 14.2\\REMRate14.exe",
                "REM/Rate v 14.2  - {blg_file}",
                "REM/Rate v 14.2",
                VersionInfo("14.2", 14, 2, 0, "rate"),
            ),
        ),
        (
            "r141",
            VersionData(
                "C:\\Program Files\\Architectural Energy Corporation\\REM Rate 14.1\\REMRate14.exe",
                "REM/Rate v 14.1  - {blg_file}",
                "REM/Rate v 14.1",
                VersionInfo("14.1", 14, 1, 0, "rate"),
            ),
        ),
        (
            "r140",
            VersionData(
                "C:\\Program Files\\Architectural Energy Corporation\\REMRate 14\\REMRate14.exe",
                "REM/Rate v 14.0  - {blg_file}",
                "REM/Rate v 14.0",
                VersionInfo("14.0", 14, 0, 0, "rate"),
            ),
        ),
    ]
)


ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_BLG = os.path.abspath(os.path.join(ROOT, "remrate", "tests/sources", "ALL FIELDS SET.blg"))

SUCCESSFUL_REGISTRATION = "REM successfully registered."


class RemRateMultipleInstancesRunning(Exception):
    pass


class RemRateWindowNotFound(Exception):
    pass


class RemRateExpectedData(Exception):
    pass


class RemRateRegistrationFailure(Exception):
    pass


class RemRateVersionIncompatibilityError(Exception):
    pass


class RemRateExe(object):
    def __init__(self, **kwargs):
        self.version_key = kwargs.get("version", get_remrate_version_key())
        self.exe_path = VERSIONS[self.version_key].exe_path
        self.title_regex = VERSIONS[self.version_key].title_regex
        self.description = VERSIONS[self.version_key].description
        self.version = VERSIONS[self.version_key].version
        self._started = False
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.filename = "Untitled.blg"

    def get_main_window(self):
        """Gets the main window"""
        title_regex = self.title_regex.format(blg_file=self.filename)
        try:
            handle = pywinauto.findwindows.find_window(title_re=title_regex)
        except findwindows.WindowAmbiguousError:
            raise RemRateMultipleInstancesRunning(
                "There are multiple copies of REM Rate running " "only one is currently allowed."
            )
        except:
            raise RemRateWindowNotFound(
                "Unable to find window matching regex - '{}'".format(title_regex)
            )
        return self.app.window_(handle=handle)

    def start(self):
        """Starts the application"""
        if self._started:
            log.warning("{} Already Started".format(self.description))
            return

        self.app = application.Application()
        assert os.path.exists(self.exe_path), "Wrong path for {} {}".format(
            self.description, self.exe_path
        )
        self.app.start_(self.exe_path)

        WaitUntilPasses(20, 0.5, lambda: self.app.window_(title_re=self.title_regex))
        log.debug("{} has started!".format(self.description))

        try:
            if self.app.RateWin.Children()[0].Texts()[0] == "OK":
                log.warning(self.app.RateWin.Children()[2].Texts()[0])
                self.app.RateWin.OKButton.Click()  # No registered user warning
        except MatchError:
            pass

        assert self.get_main_window().Exists(), "Missing Main Window!"
        self._started = True

    def close_notes(self):
        try:
            notes_window = self.app.Notes
            notes_window.SetFocus()
            notes_window.TypeKeys("%C")
        except:
            log.debug("Notes window is not active now")

    def spsheet_notes(self):
        try:
            notes_window = self.app.SpreadSheet
            notes_window.SetFocus()
            notes_window.TypeKeys("%C")
        except:
            log.debug("Spread sheet window is not active now")

    # 	for testing code
    def set_error(self):
        try:
            main = self.get_main_window()["Edit1"]
            # notes_window = self.app.ErrorWarnings
            # print(main.print_control_identifiers())
            main.SetText("Rajesh")
        except Exception as e:
            log.debug(e)

    def get_error(self):
        try:
            main = self.get_main_window()["Edit1"]
            # notes_window = self.app.ErrorWarnings
            # print(main.print_control_identifiers())
            return main.Texts()[0]
        except Exception as e:
            log.debug(e)

    def save(self, filename=DEFAULT_BLG):
        assert filename.lower().endswith(".blg"), "{} incorrect file extension".format(filename)
        main = self.get_main_window()
        main.SetFocus()
        time.sleep(1)
        main.TypeKeys("%F{DOWN 3}{ENTER}")

        try:
            open_window = self.app.SaveBuildingAs
            open_window.TypeKeys(filename, with_spaces=True)
            open_window.TypeKeys("%S")
            # For file already exist
            try:
                self.app.ConfirmSaveAs.No.Click()
                log.debug("{} File already exist".format(filename))
                open_window.Cancel.Click()
                self.save(str(time.time()) + "_" + filename)
                return
                # Need to write code for already exist and permission check
            except Exception as e:
                pass  # print(e)
            log.debug("File saved as {}".format(filename))
            self.filename = filename
            # Need to write code for already exist and permission check
        except Exception as e1:
            print(e1)
            # log.debug("{} Saved existing file".format(filename))

    def open(self, filename=DEFAULT_BLG):
        if not self._started:
            self.start()
        assert os.path.isfile(filename), "{} does not exist".format(filename)
        main = self.get_main_window()
        main.SetFocus()
        time.sleep(1)
        main.TypeKeys("%F{DOWN 1}{ENTER}")

        try:
            self.app.RateWin.No.Click()
            log.debug("Save existing - No")
        except MatchError as e:
            pass
        except Exception as e:
            log.error(e)

        try:
            self.app.LocationIsNotAvailable.Ok.Click()
            log.debug("Save existing - No")
        except MatchError as e:
            pass
        except Exception as e:
            log.error(e)

        open_window = self.app.OpenExistingBuilding
        open_window.TypeKeys(filename, with_spaces=True)
        open_window.TypeKeys("%O")
        log.debug("Loading {}".format(filename))

        # Previous Version
        try:
            alert_txt = self.app.RateWin.Static2.Texts()[0]
            log.debug(alert_txt)
            if "File was of the wrong type" in alert_txt:
                self.app.RateWin.Ok.Click()
                log.debug("Selected file was of the wrong type: {}".format(filename))
            elif "No such file or directory" in alert_txt:
                self.app.RateWin.Ok.Click()
                log.debug("No such file or directory: {}".format(filename))
            elif "Opening this building will update the building format" in alert_txt:
                self.app.RateWin.Yes.Click()
                log.debug("Opening this building will update the building format")
            else:
                self.app.RateWin.Yes.Click()
                log.debug("Created in previous version still launch - yes")
        except MatchError as e:
            pass
        except Exception as e:
            print(e)

        # Items not in library
        try:
            self.app.NotInLibrary.OKToAll.Click()
            log.debug("Items not in library add - OK")
        except MatchError as e:
            pass
        except Exception as e:
            log.error(e)

        # Items modified
        try:
            self.app.TypeHasBeenModified.OKToAll.Click()
            log.debug("Library Types have been modified - OK")
        except MatchError as e:
            pass
        except Exception as e:
            log.error(e)

        self.filename = os.path.basename(filename)
        log.debug("Using clean window name - {}".format(self.filename))

        time.sleep(2)
        log.debug("Loaded {}".format(os.path.basename(filename)))

    def get_last_update(self, default=None):
        try:
            main = self.get_main_window()
            main.SetFocus()
            last_time = main.Analysis.Children[-1].Texts[-1]
            dts = re.sub(r"Updated:", "", last_time).strip()
        except:
            raise

        if not len(dts) and default:
            date_stamp = default
        elif len(dts):
            log.debug("Baseline: {}".format(dts))
            try:
                date_stamp = dateutil.parser.parse(dts)
            except:
                raise
        else:
            return None

        log.debug("Last Update: {}".format(date_stamp))
        return date_stamp

    def get_warnings_errors(self):
        main = self.get_main_window()
        main.SetFocus()
        counter, texts = 0, []
        while True:
            if counter > 20:
                break
            texts = main.ErrorsWarnings.Children[0].Texts
            if len(texts):
                break
            time.sleep(0.1)
            counter += 1

        if len(texts) > 2:
            texts = texts[1:]
            issues = "\n".join(texts[1:]).split("\n\n")
        else:
            return None

        if "ERROR" in texts[0]:
            log.error(issues)
        if "WARNING" in texts[0]:
            log.warning(repr(issues))
        return issues

    def simulate(self):
        start = self.get_last_update(default=datetime.datetime.now())
        time.sleep(0.5)

        main = self.get_main_window()
        main.SetFocus()
        main.TypeKeys("%RQ")

        counter = 0
        while True:
            updated = self.get_last_update()
            if (updated and updated > start) or counter > 200:
                break
            time.sleep(0.2)
            counter += 1

        issues = self.get_warnings_errors()
        log.debug("Simulation done.. {} issues".format(len(issues)))

    def set_user(self, username=None, password=None):
        """Sets the user and password - validates it works"""
        if not self._started:
            self.start()

        username = username if username else self.username if self.username else "MALICIOUS USER"
        password = password if password else self.password if self.password else "LET ME IN"

        main = self.get_main_window()
        main.SetFocus()
        main.TypeKeys("%T{DOWN 7}{RIGHT}{ENTER}")

        WaitUntilPasses(20, 0.5, lambda: self.app.window_(title_re="Register REM"))

        log.debug("Registering {}/{}".format(username, password))
        register_window = self.app.RegisterREM
        register_window.TypeKeys(username, with_spaces=True)
        register_window.TypeKeys("{TAB}")
        register_window.TypeKeys(password, with_spaces=True)
        register_window.TypeKeys("{TAB}{ENTER}")

        counter, texts = 0, []
        while True:
            if counter > 20:
                break
            try:
                texts = self.app.RateWin.Children()[-1].Texts()
                if len(texts):
                    self.app.RateWin.OKButton.Click()
                    break
            except Exception:
                pass
            time.sleep(0.1)
            counter += 1
        if not texts:
            raise RemRateExpectedData("We were expecting to see a registration window.")
        if not texts[0].startswith(SUCCESSFUL_REGISTRATION):
            register_window.CancelButton.Click()
            log.warning(texts[0])
            raise RemRateRegistrationFailure(texts[0])
        log.info(texts[0])
        return texts[0]

    def about(self):
        if not self._started:
            self.start()

        main = self.get_main_window()
        main.SetFocus()
        main.TypeKeys("%H{DOWN 5}{ENTER}")

        about = self.app.AboutREMRate
        assert about.Exists(), "Missing about window"

        data = about.Children()[1].Texts()[0].split("\n")

        data = [x.strip() for x in data]
        version = data[0].split(" ")[-1]
        account_type = data[1].split(":")[-1].strip()
        expires = dateutil.parser.parse(data[2].split(":")[-1].strip())

        about.CloseButton.Click()
        log.debug(
            "{} version: {} account type: {} expires: {}".format(
                self.description, version, account_type, expires
            )
        )
        return {"account_type": account_type, "expires": expires, "version": version}

    def exit(self):
        if not self._started:
            self.start()

        main = self.get_main_window()
        main.SetFocus()
        main.TypeKeys("%F{UP}{ENTER}")

        # Save it.
        try:
            self.app.RateWin.No.Click()
            log.debug("Don't save it")
        except:
            pass

        time.sleep(1)
        self._started = False
        self.filename = "Untitled.blg"
        log.info("Shutdown {}".format(self.description))

    def export(self, user_id, passwd):
        main = self.get_main_window()
        main.SetFocus()
        time.sleep(1)
        main.TypeKeys("%T{RIGHT 1}{ENTER}")
        try:
            self.app.ExportDatabaseSetup.RadioButton2.Click()
            self.app.ExportDatabaseSetup.Select.Click()
            self.app.SQLDatabaseConnectionSetup.Listbox.Select("Mysql32")  # self.version_key)
            # self.app.SQLDatabaseConnectionSetup.edit1.SetText("Mysql32")  #self.version_key)
            self.app.SQLDatabaseConnectionSetup.edit2.SetText(user_id)
            self.app.SQLDatabaseConnectionSetup.edit3.SetText(passwd)
            self.app.SQLDatabaseConnectionSetup.Ok.Click()
            self.app.ExportDatabaseSetup.Ok.Click()
            time.sleep(5)
            try:
                if self.app.RateWin.OK.Texts()[0] == "OK":
                    alert_txt = str(self.app.RateWin.Static2.Texts()[0])
                    log.warning(alert_txt)
                    self.app.RateWin.OKButton.Click()  # No registered user warning
                    if alert_txt.find(
                        "version of the software, and is incompatible with the current routines."
                    ):
                        self.app.ExportDatabaseSetup.Cancel.Click()
            except MatchError:
                pass
            except Exception as e:
                log.error(e)
        except MatchError:
            pass
        except Exception as e:
            log.error(e)

    def export_xml(self, filename):
        if not self.version_check(14, 5, 1):
            raise RemRateVersionIncompatibilityError("Unable to export must be > 14.5.1")

        main = self.get_main_window()
        main.SetFocus()
        time.sleep(1)
        main.TypeKeys("%F{DOWN 9}{ENTER}")

        try:
            open_window = self.app.Export
            open_window.TypeKeys(filename, with_spaces=True)
            open_window.TypeKeys("%S")

            try:
                self.app.Export.Ok.Click()
                open_window.Cancel.Click()
                log.debug("{} File name is not valid ".format(filename))
                return True
            except MatchError as e:
                pass
            except Exception as e:
                log.error(e)

            # For file already exist
            try:
                self.app.ConfirmSaveAs.No.Click()
                log.debug("{} File already exist".format(filename))
                open_window.Cancel.Click()
                self.export_xml(str(time.time()) + "_" + filename)
                return True
                # Need to write code for already exist and permission check
            except MatchError as e:
                pass
            except Exception as e:
                log.error(e)

            log.debug("File saved as {}".format(filename))
            # Need to write code for already exist and permission check
        except MatchError as e:
            log.info("Export Building to xml menu is disabled")
            main.SetFocus()
            time.sleep(1)
            main.TypeKeys("{ESC}")
        except Exception as exp:
            log.error(exp)

    def version_check(self, major, minor, patch=None, flavor=None):
        if flavor and self.version.flavor != flavor:
            log.debug("Wrong flavor {} {}".format(self.version.flavor, flavor))
            return False

        if self.version.major < major:
            log.debug("Wrong major {} {}".format(self.version.major, major))
            return False
        elif self.version.major > major:
            return True
        else:
            if self.version.minor < minor:
                log.debug("Wrong minor {} {}".format(self.version.minor, minor))
                return False
            elif self.version.minor > minor:
                return True
            else:
                if not patch:
                    return True
                else:
                    if self.version.patch < patch:
                        log.debug("Wrong patch {} {}".format(self.version.patch, patch))
                        return False
                    return True


def kill_remrate(version_key=None):
    """This will kill remrate"""

    if version_key is None:
        version_keys = VERSIONS.keys()
    else:
        version_keys = [version_key]

    versions = list(set([os.path.basename(VERSIONS[v].exe_path) for v in version_keys]))

    for process in psutil.get_process_list():
        try:
            if process.name() in versions:
                log.error("Killing {} [{}]".format(process.name(), process.pid))
                process.kill()
        except psutil.AccessDenied:
            pass


def get_remrate_version_key(major=None, minor=None, patch=None, flavor="rate", label=None):
    """This will return the version key"""
    # Always return the latest version
    if major is None:
        major = max([x.version.major for x in VERSIONS.values() if x.version.flavor == flavor])
    if minor is None:
        minor = max(
            [
                x.version.minor
                for x in VERSIONS.values()
                if x.version.major == major and x.version.flavor == flavor
            ]
        )
    if patch is None:
        patch = max(
            [
                x.version.patch
                for x in VERSIONS.values()
                if x.version.major == major
                and x.version.minor == minor
                and x.version.flavor == flavor
            ]
        )

    return next(
        (
            k
            for k, x in VERSIONS.items()
            if x.version.major == major
            and x.version.minor == minor
            and x.version.patch == patch
            and x.version.flavor == flavor
        ),
        None,
    )


def main(data):
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        level=logging.DEBUG,
    )

    log.debug("Here we go..")

    # remrate = RemRateExe()
    # remrate.open(data.get('file'))
    # remrate.simulate()
    # remrate.export()
    # remrate.exit()

    remrate = RemRateExe()
    remrate.set_user(username="4BxMdU", password="t7pUsZ")  # nosec
    print(remrate.get_user_details())
    remrate.exit()

    pprint.pprint(data)


if __name__ == "__main__":
    data = {"version": "r1451", "file": DEFAULT_BLG}

    sys.exit(main(data))
