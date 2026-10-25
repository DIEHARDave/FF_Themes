#!/bin/sh
# FF_Themes installer for Zmod. Run by Zmod's ENABLE_PLUGIN; safe to run
# again. (On Kiln OS this script isn't used: extras/ff_themes.py installs
# the themes when Klipper starts.)
#
# Mainsail loads its theme from config/.theme and Fluidd from
# config/.fluidd-theme, which Zmod keeps as links to mod_data/.theme and
# mod_data/.fluidd-theme. Those folders become links to the themes in this
# plugin for this printer, so updates arrive through the update manager.
# Whatever was in them before is moved to mod_data/ff_themes_backup and put
# back by uninstall.sh.

MOD_DATA="/opt/config/mod_data"
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

# Another theme plugin (zmod_ad5x_theme) holds the user's backup; its
# uninstall has to put that back first.
case "$(readlink "${MOD_DATA}/.theme")" in
    "${PLUGIN}"/*) ;;
    plugins/*)
        other="$(readlink "${MOD_DATA}/.theme")"
        other="${other#plugins/}"
        echo "ff_themes: the ${other%%/*} plugin's theme is installed."
        echo "ff_themes: run DISABLE_PLUGIN name=${other%%/*} first, then ENABLE_PLUGIN name=ff_themes again."
        exit 1
        ;;
esac

# link_theme FOLDER SOURCE UI: link mod_data/FOLDER to SOURCE in this plugin.
link_theme() {
    theme="${MOD_DATA}/$1"
    target="${PLUGIN}/$2"
    backup="${BACKUP_DIR}/$1"
    current="$(readlink "$theme")"
    case "$current" in
        "$target")
            echo "ff_themes: $3 theme already installed (${NAME})"
            return
            ;;
        "${PLUGIN}"/*)
            # This plugin's link to another theme; the backup stays as it is.
            ;;
        *)
            mkdir -p "$BACKUP_DIR"
            if [ -e "$theme" ] || [ -L "$theme" ]; then
                if [ -e "$backup" ] || [ -L "$backup" ]; then
                    # The older backup is the theme from before the first install;
                    # keep it as the one to restore and set this one aside with a date.
                    aside="${backup}.$(date +%Y%m%d_%H%M%S)"
                    mv "$theme" "$aside"
                    echo "ff_themes: existing $3 theme moved to $aside"
                else
                    mv "$theme" "$backup"
                    echo "ff_themes: existing $3 theme backed up to $backup"
                fi
            fi
            ;;
    esac
    # Relative, so it resolves both on the printer and inside Zmod's chroot.
    ln -sfn "$target" "$theme"
    echo "ff_themes: $3 theme ${NAME} installed"
}

link_theme .theme "themes/${NAME}" Mainsail
[ -d "${MOD_DATA}/${PLUGIN}/fluidd-themes/${NAME}" ] &&
    link_theme .fluidd-theme "fluidd-themes/${NAME}" Fluidd

# Zmod sets these links on boot; set them now so the themes show without one.
[ "$(readlink /opt/config/.theme)" = "mod_data/.theme" ] || ln -sfn mod_data/.theme /opt/config/.theme
[ "$(readlink /opt/config/.fluidd-theme)" = "mod_data/.fluidd-theme" ] || ln -sfn mod_data/.fluidd-theme /opt/config/.fluidd-theme

echo "ff_themes: reload Mainsail / Fluidd in your browser (Ctrl+F5)"
