# FF_Themes

Mainsail themes for Flashforge printers, as one plugin that works on both
[Zmod](https://github.com/ghzserg/zmod) and [Kiln OS](https://github.com/djvalic/kiln-os).
It picks the theme for the printer it's installed on and keeps it up to
date through the update manager.

| Firmware | Printer | Theme folder |
| :--- | :--- | :--- |
| Zmod | AD5X | `themes/zmod-ad5x` |
| Zmod | Creator 5 Pro | `themes/zmod-c5` |
| Kiln OS | AD5X | `themes/kiln-ad5x` |

Each theme folder holds what Mainsail looks for in the hidden `.theme`
folder in the config files:

| File | What it is |
| :--- | :--- |
| `sidebar-logo.svg` | Logo at the top of the sidebar |
| `sidebar-background.png` | Sidebar background |
| `main-background.png` | Page background |
| `custom.css` | Zmod themes only: Zmod's dialog button fix; Zmod also checks for this file on boot |

## Zmod

### Install

Add this to `mod_data/user.moonraker.conf`:

```ini
[update_manager ff_themes]
type: git_repo
channel: stable
path: /root/printer_data/config/mod_data/plugins/ff_themes
origin: https://github.com/DIEHARDave/FF_Themes.git
is_system_service: False
primary_branch: main
```

Then run `ENABLE_PLUGIN name=ff_themes` in the console and reload Mainsail
with Ctrl+F5. Zmod restarts Klipper's firmware after enabling a plugin, so
don't enable it during a print.

The installer reads Zmod's printer settings (`AD5X=1` or `C5PRO=1`) and
links the matching theme. On any other printer it stops without changing
anything; run `DISABLE_PLUGIN name=ff_themes` to take it out of the plugin
list again.

Coming from `zmod_ad5x_theme`? Run `DISABLE_PLUGIN name=zmod_ad5x_theme`
first, so it puts your old theme back, then enable `ff_themes`. The
installer stops and tells you to do this if it finds the old plugin's theme.

### Uninstall

Run `DISABLE_PLUGIN name=ff_themes`. Your previous theme comes back, or
Zmod's default if you didn't have one.

### Your existing theme

The installer never deletes a theme. Zmod keeps the theme in
`mod_data/.theme`. If that folder exists, it is moved to
`mod_data/ff_themes_backup/` before the plugin's theme goes in, and
`DISABLE_PLUGIN` moves it back.

If you install again later and find a theme folder that isn't the
plugin's, the first backup stays the one that gets restored. The newer
folder is set aside next to it with the date added to its name.

| Path | What it is |
| :--- | :--- |
| `config/.theme` | Zmod's link to `mod_data/.theme`; left as it is. |
| `config/mod_data/.theme` | Link to this plugin's theme for the printer. |
| `config/mod_data/ff_themes_backup/` | The theme that was there before, if any. |

## Kiln OS

### Install

Over SSH as root (Kiln's default password is `root`):

```sh
cd /data/ad5x/plugins
su klipper -s /bin/sh -c 'git clone https://github.com/DIEHARDave/FF_Themes.git ff_themes'
```

Then in the console (Mainsail, Fluidd or HelixScreen):

```
ENABLE_PLUGIN NAME=ff_themes
```

Klipper restarts and copies the theme into the config folder's `.theme`.
Reload Mainsail with Ctrl+F5. Software Updates now lists `ff_themes`.
Nothing runs as root.

Kiln plugins have no install script, so the plugin's Klipper module
(`extras/ff_themes.py`) does the work each time Klipper starts: it copies
any theme file that changed and removes files that aren't part of the
theme. After an update, run `RESTART` to pick up new theme files.

| Command | What it does |
| :--- | :--- |
| `FF_THEME` | Shows the installed theme and whether a backup is waiting |
| `FF_THEME_RESTORE` | Puts back the theme from before the plugin; run it before `DISABLE_PLUGIN` |

### Uninstall

```
FF_THEME_RESTORE
DISABLE_PLUGIN NAME=ff_themes
```

`FF_THEME_RESTORE` has to come first. Once the plugin is off, its module
no longer loads, so nothing is left to restore the old theme. If you
disable it without restoring, the plugin's theme just stays where it is,
and your old theme is still in `config/ff_themes_backup/.theme`.

### Your existing theme

The theme Kiln shows is a plain `.theme` folder in the config files. The
plugin marks its own copy with a `.ff_themes` file. Any other `.theme` is
moved to `config/ff_themes_backup/` before the plugin's theme goes in. As
on Zmod, the first backup is the one that gets restored; a later one is
set aside next to it with the date added to its name.

## Without the plugin

The themes are plain files, so you can also put them on the printer by
hand. They won't update by themselves then. Don't do both: if the plugin
is on, uninstall it first (see above). On Zmod a hand upload would write
into the plugin's folder through its link; on Kiln the plugin replaces the
files at the next Klipper start.

### Get the files

Open the theme folder for your printer on GitHub (`themes/zmod-ad5x`,
`themes/zmod-c5` or `themes/kiln-ad5x`) and download each file with the
"Download raw file" button. Or use **Code > Download ZIP** and unzip it.

You need every file in that folder. On Zmod, `custom.css` matters: when
Zmod boots and `.theme` has no `custom.css`, it copies its default theme
back over the folder, and your logo goes with it.

### Upload through Mainsail

1. Open **Machine** in Mainsail.
2. In the **Config Files** panel, click the gear icon and turn on
   **Show hidden files**.
3. If there is no `.theme` folder, create it with the create-folder
   button (folder icon) and name it `.theme`.
4. Open `.theme` and upload the theme files with the upload button. Let
   them replace the files that are already there.
5. Reload Mainsail with Ctrl+F5.

On Zmod, `.theme` in the config root is a link to `mod_data/.theme`, so the
files end up there. That's expected.

### Copy with scp

| Firmware | Folder on the printer |
| :--- | :--- |
| Zmod (AD5X, Creator 5 Pro) | `/opt/config/mod_data/.theme/` |
| Kiln OS | `/home/klipper/printer_data/config/.theme/` |

Neither printer has an SFTP server, so use `scp -O` (the old scp protocol).
The default password is `root` on both. From the unzipped theme folder:

```sh
# Zmod
ssh root@<printer> 'mkdir -p /opt/config/mod_data/.theme'
scp -O * root@<printer>:/opt/config/mod_data/.theme/

# Kiln OS
ssh root@<printer> 'mkdir -p /home/klipper/printer_data/config/.theme'
scp -O * root@<printer>:/home/klipper/printer_data/config/.theme/
ssh root@<printer> 'cd /home/klipper/printer_data/config && chown -R klipper:klipper .theme && chmod -R a+rX .theme'
```

The last line matters on Kiln: files copied in as root are owned by root
and readable only by root, so Moonraker, which runs as `klipper`, can't
serve them to Mainsail.

Reload Mainsail with Ctrl+F5.

## Adding a theme

1. Add a folder under `themes/`.
2. On Zmod, pick it in `install.sh` from the settings in Zmod's `0.sh`.
   Zmod themes need a `custom.css`, or Zmod's boot script writes one
   through the link into this repository.
3. On Kiln, set `theme:` under `[ff_themes]` in `plugin.cfg`.

## License

GPL-3.0, see [LICENSE](LICENSE).
