#!/bin/sh
# Run by Zmod's DISABLE_PLUGIN. Puts back the themes that install.sh backed
# up, or Zmod's default themes if there weren't any.

MOD_DATA="/opt/config/mod_data"
PLUGIN="plugins/ff_themes"
BACKUP_DIR="${MOD_DATA}/ff_themes_backup"

# Newer Zmod keeps its scripts in /usr/data/zmod, older versions in mod/.
ZSHELL=/usr/data/zmod/zmod/.shell
[ -d "${ZSHELL}/.theme" ] || ZSHELL=/opt/config/mod/.shell

# unlink_theme FOLDER UI: undo link_theme in install.sh.
unlink_theme() {
    theme="${MOD_DATA}/$1"
    backup="${BACKUP_DIR}/$1"
    case "$(readlink "$theme")" in
        "${PLUGIN}"/*) rm -f "$theme" ;;
        # A theme this plugin never replaced (no backup either): leave it.
        *) if [ -e "$theme" ] && ! [ -e "$backup" ] && ! [ -L "$backup" ]; then
               return 0
           fi ;;
    esac

    if [ -e "$theme" ] || [ -L "$theme" ]; then
        # Something other than this plugin's link is in place; don't overwrite it.
        echo "ff_themes: $theme was replaced after install; kept it."
        [ -e "$backup" ] && echo "ff_themes: the old one is still in $backup"
    elif [ -e "$backup" ] || [ -L "$backup" ]; then
        mv "$backup" "$theme"
        echo "ff_themes: restored the previous $2 theme"
    else
        # Zmod would copy its default back on the next boot; do it now.
        cp -a "${ZSHELL}/$1" "$MOD_DATA/"
        echo "ff_themes: restored Zmod's default $2 theme"
    fi
}

unlink_theme .theme Mainsail
unlink_theme .fluidd-theme Fluidd

# Leaves the folder if it still holds a set-aside theme.
rmdir "$BACKUP_DIR" 2> /dev/null

echo "ff_themes: removed. Reload Mainsail / Fluidd in your browser (Ctrl+F5)"
