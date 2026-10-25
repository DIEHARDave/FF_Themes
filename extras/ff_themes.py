# FF_Themes on Kiln OS: puts this plugin's Mainsail theme in the config
# folder's .theme when Klipper starts (Kiln plugins have no install
# script), FF_THEME shows the state, FF_THEME_RESTORE puts the old theme
# back before DISABLE_PLUGIN.
#
# The files are copied, not linked: the plugin lives in /data/ad5x/plugins,
# outside the folders Moonraker serves. A marker file in .theme says the
# copy is ours; any other .theme is moved to ff_themes_backup first.
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

def same_file(a, b):
    try:
        if os.path.getsize(a) != os.path.getsize(b):
            return False
        with open(a, "rb") as fa, open(b, "rb") as fb:
            return fa.read() == fb.read()
    except OSError:
        return False

class FFThemes:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get("theme", "kiln-ad5x")
        self.source = os.path.join(PLUGIN_DIR, "themes", self.name)
        cfg = self.printer.get_start_args()["config_file"]
        cfgdir = os.path.dirname(os.path.abspath(cfg))
        self.theme = os.path.join(cfgdir, ".theme")
        self.backup_dir = os.path.join(cfgdir, "ff_themes_backup")
        self.backup = os.path.join(self.backup_dir, ".theme")
        if not os.path.isdir(self.source):
            raise config.error("ff_themes: no theme named '%s' (themes/: %s)"
                               % (self.name, ", ".join(self.themes())))
        try:
            self.state = self.install()
        except OSError as e:
            logging.exception("ff_themes: install failed")
            self.state = "install failed: %s" % (e,)
        logging.info("ff_themes: %s", self.state)
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command("FF_THEME", self.cmd_FF_THEME,
                               desc="Show the FF_Themes Mainsail theme state")
        gcode.register_command("FF_THEME_RESTORE", self.cmd_FF_THEME_RESTORE,
                               desc="Put back the theme from before FF_Themes"
                               " (run before DISABLE_PLUGIN NAME=ff_themes)")

    def themes(self):
        try:
            return sorted(os.listdir(os.path.join(PLUGIN_DIR, "themes")))
        except OSError:
            return []

    def ours(self):
        return os.path.isfile(os.path.join(self.theme, MARK))

    def install(self):
        msg = []
        if os.path.lexists(self.theme) and not self.ours():
            os.makedirs(self.backup_dir, exist_ok=True)
            if os.path.lexists(self.backup):
                # The older backup is the theme from before the first
                # install; keep it as the one to restore.
                dest = "%s.%s" % (self.backup, time.strftime("%Y%m%d_%H%M%S"))
            else:
                dest = self.backup
            shutil.move(self.theme, dest)
            msg.append("existing theme moved to %s" % (dest,))
        os.makedirs(self.theme, exist_ok=True)
        wanted = set(os.listdir(self.source))
        changed = 0
        for fn in sorted(wanted):
            src = os.path.join(self.source, fn)
            dst = os.path.join(self.theme, fn)
            if os.path.isfile(src) and not same_file(src, dst):
                shutil.copyfile(src, dst)
                changed += 1
        for fn in os.listdir(self.theme):
            if fn != MARK and fn not in wanted:
                path = os.path.join(self.theme, fn)
                if os.path.isdir(path) and not os.path.islink(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                changed += 1
        with open(os.path.join(self.theme, MARK), "w") as f:
            f.write("%s\n" % (self.name,))
        msg.append("theme %s %s" % (self.name, "updated" if changed
                                    else "up to date"))
        return "; ".join(msg)

    def cmd_FF_THEME(self, gcmd):
        lines = ["FF_Themes: %s" % (self.state,),
                 "Installed: %s" % ("yes" if self.ours() else "no"),
                 "Themes: %s" % (", ".join(self.themes()),)]
        if os.path.lexists(self.backup):
            lines.append("Backup to restore: %s" % (self.backup,))
        gcmd.respond_info("\n".join(lines))

    def cmd_FF_THEME_RESTORE(self, gcmd):
        if not self.ours():
            raise gcmd.error("FF_Themes: %s isn't this plugin's theme;"
                             " nothing changed" % (self.theme,))
        shutil.rmtree(self.theme)
        if os.path.lexists(self.backup):
            shutil.move(self.backup, self.theme)
            done = "restored the previous theme"
        else:
            done = "removed the theme (there was none before)"
        try:
            # Leaves the folder if it still holds a set-aside theme.
            os.rmdir(self.backup_dir)
        except OSError:
            pass
        self.state = done
        gcmd.respond_info("FF_Themes: %s. Now run DISABLE_PLUGIN"
                          " NAME=ff_themes (or RESTART puts the theme back),"
                          " then reload Mainsail (Ctrl+F5)." % (done,))

def load_config(config):
    return FFThemes(config)
