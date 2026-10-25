#!/bin/sh
# FF_Themes installer for Zmod. Run by Zmod's ENABLE_PLUGIN; safe to run
# again. (On Kiln OS this script isn't used: extras/ff_themes.py installs
# the theme when Klipper starts.)
#
# Mainsail loads its theme from config/.theme, which Zmod keeps as a link to
# mod_data/.theme. That folder becomes a link to the theme in this plugin
# for this printer, so updates arrive through the update manager. Whatever
# was in it before is moved to mod_data/ff_themes_backup and put back by
# uninstall.sh.

MOD_DATA="/opt/config/mod_data"
THEME="${MOD_DATA}/.theme"
PLUGIN="plugins/ff_themes"
BACKUP_DIR="${MOD_DATA}/ff_themes_backup"

# Zmod's printer settings: AD5X=1 on the AD5X, C5PRO=1 on the Creator 5
# Pro. Newer Zmod keeps its scripts in /usr/data/zmod, older versions in mod/.
ZSHELL=/usr/data/zmod/zmod/.shell
[ -f "${ZSHELL}/0.sh" ] || ZSHELL=/opt/config/mod/.shell
. "${ZSHELL}/0.sh"
if [ "${AD5X}" = 1 ]; then
    NAME=zmod-ad5x
elif [ "${C5PRO}" = 1 ]; then
    NAME=zmod-c5
else
    echo "ff_themes: no theme for this printer yet (AD5X and Creator 5 Pro only); nothing changed."
    echo "ff_themes: run DISABLE_PLUGIN name=ff_themes to remove it."
    exit 1
fi
TARGET="${PLUGIN}/themes/${NAME}"

current="$(readlink "$THEME")"
case "$current" in
    "$TARGET")
        echo "ff_themes: already installed (${NAME})"
        ;;
    "${PLUGIN}"/*)
        # This plugin's link to another theme; the backup stays as it is.
        ln -sfn "$TARGET" "$THEME"
        echo "ff_themes: switched to ${NAME}"
        ;;
    plugins/*)
        # Another theme plugin (zmod_ad5x_theme) holds the user's backup;
        # its uninstall has to put that back first.
        other="${current#plugins/}"
        echo "ff_themes: the ${other%%/*} plugin's theme is installed."
        echo "ff_themes: run DISABLE_PLUGIN name=${other%%/*} first, then ENABLE_PLUGIN name=ff_themes again."
        exit 1
        ;;
    *)
        mkdir -p "$BACKUP_DIR"
        if [ -e "$THEME" ] || [ -L "$THEME" ]; then
            if [ -e "${BACKUP_DIR}/.theme" ] || [ -L "${BACKUP_DIR}/.theme" ]; then
                # The older backup is the theme from before the first install;
                # keep it as the one to restore and set this one aside with a date.
                aside="${BACKUP_DIR}/.theme.$(date +%Y%m%d_%H%M%S)"
                mv "$THEME" "$aside"
                echo "ff_themes: existing theme moved to $aside"
            else
                mv "$THEME" "${BACKUP_DIR}/.theme"
                echo "ff_themes: existing theme backed up to ${BACKUP_DIR}/.theme"
            fi
        fi
        # Relative, so it resolves both on the printer and inside Zmod's chroot.
        ln -sfn "$TARGET" "$THEME"
        echo "ff_themes: installed ${NAME}"
        ;;
esac

# Zmod sets this link on boot; set it now so the theme shows without one.
[ "$(readlink /opt/config/.theme)" = "mod_data/.theme" ] || ln -sfn mod_data/.theme /opt/config/.theme

echo "ff_themes: reload Mainsail in your browser (Ctrl+F5)"
