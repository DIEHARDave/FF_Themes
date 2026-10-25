# FF_Themes on Kiln OS: puts this plugin's Mainsail theme in the config
# folder's .theme, and its Fluidd theme (if it has one) in .fluidd-theme,
# when Klipper starts (Kiln plugins have no install script). FF_THEME
# shows the state, FF_THEME_RESTORE puts the old themes back before
# DISABLE_PLUGIN.
#
# The files are copied, not linked: the plugin lives in /data/ad5x/plugins,
# outside the folders Moonraker serves. A marker file in each folder says
# the copy is ours; any other folder is moved to ff_themes_backup first.
#
# Copyright (C) 2026  DIEHARDave
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import os
import shutil
import time

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = ".ff_themes"
# (folder in this plugin, folder in the config directory, UI)
KINDS = (("themes", ".theme", "Mainsail"),
         ("fluidd-themes", ".fluidd-theme", "Fluidd"))

def same_file(a, b):
    try:
        if os.path.getsize(a) != os.path.getsize(b):
            return False
        with open(a, "rb") as fa, open(b, "rb") as fb:
            return fa.read() == fb.read()
    except OSError:
        return False

class ThemeDir:
    """One theme folder in the config directory and the plugin's source
    for it."""
    def __init__(self, source, target, backup, ui):
        self.source = source
        self.target = target
        self.backup = backup
        self.ui = ui

    def ours(self):
        return os.path.isfile(os.path.join(self.target, MARK))

    def install(self, name):
        msg = []
        if os.path.lexists(self.target) and not self.ours():
            os.makedirs(os.path.dirname(self.backup), exist_ok=True)
            if os.path.lexists(self.backup):
                # The older backup is the theme from before the first
                # install; keep it as the one to restore.
                dest = "%s.%s" % (self.backup, time.strftime("%Y%m%d_%H%M%S"))
            else:
                dest = self.backup
            shutil.move(self.target, dest)
            msg.append("existing %s theme moved to %s" % (self.ui, dest))
        os.makedirs(self.target, exist_ok=True)
        wanted = set(os.listdir(self.source))
        changed = 0
        for fn in sorted(wanted):
            src = os.path.join(self.source, fn)
            dst = os.path.join(self.target, fn)
            if os.path.isfile(src) and not same_file(src, dst):
                shutil.copyfile(src, dst)
                changed += 1
        for fn in os.listdir(self.target):
            if fn != MARK and fn not in wanted:
                path = os.path.join(self.target, fn)
                if os.path.isdir(path) and not os.path.islink(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                changed += 1
        with open(os.path.join(self.target, MARK), "w") as f:
            f.write("%s\n" % (name,))
        msg.append("%s theme %s %s" % (self.ui, name, "updated" if changed
                                       else "up to date"))
        return msg

    def restore(self):
        if not self.ours():
            return None
        shutil.rmtree(self.target)
        if os.path.lexists(self.backup):
            shutil.move(self.backup, self.target)
            return "restored the previous %s theme" % (self.ui,)
        return "removed the %s theme (there was none before)" % (self.ui,)

class FFThemes:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get("theme", "kiln-ad5x")
        cfg = self.printer.get_start_args()["config_file"]
        cfgdir = os.path.dirname(os.path.abspath(cfg))
        self.backup_dir = os.path.join(cfgdir, "ff_themes_backup")
        self.dirs = []
        for src, target, ui in KINDS:
            source = os.path.join(PLUGIN_DIR, src, self.name)
            if os.path.isdir(source):
                self.dirs.append(ThemeDir(
                    source, os.path.join(cfgdir, target),
                    os.path.join(self.backup_dir, target), ui))
        if not self.dirs or self.dirs[0].ui != "Mainsail":
            raise config.error("ff_themes: no theme named '%s' (themes/: %s)"
                               % (self.name, ", ".join(self.themes())))
        msg = []
        for d in self.dirs:
            try:
                msg += d.install(self.name)
            except OSError as e:
                logging.exception("ff_themes: %s install failed", d.ui)
                msg.append("%s install failed: %s" % (d.ui, e))
        self.state = "; ".join(msg)
        logging.info("ff_themes: %s", self.state)
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command("FF_THEME", self.cmd_FF_THEME,
                               desc="Show the FF_Themes theme state")
        gcode.register_command("FF_THEME_RESTORE", self.cmd_FF_THEME_RESTORE,
                               desc="Put back the themes from before FF_Themes"
                               " (run before DISABLE_PLUGIN NAME=ff_themes)")

    def themes(self):
        try:
            return sorted(os.listdir(os.path.join(PLUGIN_DIR, "themes")))
        except OSError:
            return []

    def cmd_FF_THEME(self, gcmd):
        lines = ["FF_Themes: %s" % (self.state,)]
        for d in self.dirs:
            lines.append("%s: %s" % (d.ui, "installed" if d.ours()
                                     else "not installed"))
            if os.path.lexists(d.backup):
                lines.append("%s backup to restore: %s" % (d.ui, d.backup))
        lines.append("Themes: %s" % (", ".join(self.themes()),))
        gcmd.respond_info("\n".join(lines))

    def cmd_FF_THEME_RESTORE(self, gcmd):
        done = [m for m in (d.restore() for d in self.dirs) if m]
        if not done:
            raise gcmd.error("FF_Themes: no theme of this plugin is"
                             " installed; nothing changed")
        try:
            # Leaves the folder if it still holds a set-aside theme.
            os.rmdir(self.backup_dir)
        except OSError:
            pass
        self.state = "; ".join(done)
        gcmd.respond_info("FF_Themes: %s. Now run DISABLE_PLUGIN"
                          " NAME=ff_themes (or RESTART puts the themes back),"
                          " then reload the page (Ctrl+F5)." % (self.state,))

def load_config(config):
    return FFThemes(config)
