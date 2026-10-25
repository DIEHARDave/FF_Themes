#!/bin/sh
# Run by Zmod's DISABLE_PLUGIN. Puts back the theme that install.sh backed
# up, or Zmod's default theme if there wasn't one.

MOD_DATA="/opt/config/mod_data"
THEME="${MOD_DATA}/.theme"
PLUGIN="plugins/ff_themes"
BACKUP_DIR="${MOD_DATA}/ff_themes_backup"

case "$(readlink "$THEME")" in
    "${PLUGIN}"/*) rm -f "$THEME" ;;
esac

if [ -e "$THEME" ] || [ -L "$THEME" ]; then
    # Something other than this plugin's link is in place; don't overwrite it.
    echo "ff_themes: $THEME was replaced after install; kept it."
    [ -e "${BACKUP_DIR}/.theme" ] && echo "ff_themes: the old one is still in ${BACKUP_DIR}/.theme"
elif [ -e "${BACKUP_DIR}/.theme" ] || [ -L "${BACKUP_DIR}/.theme" ]; then
    mv "${BACKUP_DIR}/.theme" "$THEME"
    echo "ff_themes: restored the previous theme"
else
    # Zmod would copy its default back on the next boot; do it now.
    # Newer Zmod keeps its scripts in /usr/data/zmod, older versions in mod/.
    ZSHELL=/usr/data/zmod/zmod/.shell
    [ -d "${ZSHELL}/.theme" ] || ZSHELL=/opt/config/mod/.shell
    cp -a "${ZSHELL}/.theme" "$MOD_DATA/"
    echo "ff_themes: restored Zmod's default theme"
fi

# Leaves the folder if it still holds a set-aside theme.
rmdir "$BACKUP_DIR" 2> /dev/null

echo "ff_themes: removed. Reload Mainsail in your browser (Ctrl+F5)"
