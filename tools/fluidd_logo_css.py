#!/usr/bin/env python3
# Writes a Fluidd custom.css that shows a theme's sidebar-logo.svg in the
# top bar instead of Fluidd's logo, and optionally another logo in place of
# the faint one in the page's bottom right corner. Fluidd reads only
# custom.css and background.* from .fluidd-theme, so the logos go in as
# data URIs. --base puts another stylesheet first (Zmod's own Fluidd
# custom.css, which Zmod expects to find there).
#
#   python3 tools/fluidd_logo_css.py themes/kiln-ad5x/sidebar-logo.svg \
#       fluidd-themes/kiln-ad5x/custom.css \
#       --background logos/kiln-os-icon-background.svg
#   python3 tools/fluidd_logo_css.py themes/zmod-ad5x/sidebar-logo.svg \
#       fluidd-themes/zmod-ad5x/custom.css --base tools/zmod-fluidd-base.css
import argparse
import base64

CSS = """\
/* FF_Themes: {name} in Fluidd's top bar. Made by tools/fluidd_logo_css.py
   from the Mainsail theme's sidebar-logo.svg; edit that and run it again. */
.toolbar-logo {{
  width: auto !important;
  padding: 0 10px;
}}
.logo-wrapper svg {{
  display: none !important;
}}
.logo-wrapper {{
  width: 100px;
  height: 48px;
  background: url("data:image/svg+xml;base64,{data}") center / contain no-repeat;
}}
"""

# Fluidd's background logo is an inline <svg class="background-logo">
# (shown when "Show background logo" is on in Fluidd's theme settings):
# hide its paths and paint the new logo as the element's background.
# Fluidd fades the whole element to 8% and lets it hang well off the
# corner; here it is fully opaque, so the logo file carries its own
# transparency per color, and smaller and closer to the corner.
BACKGROUND_CSS = """\
/* Bottom right background logo, from {name}. */
.background-logo > * {{
  display: none !important;
}}
.background-logo {{
  opacity: 1 !important;
  width: 26% !important;
  right: -2% !important;
  bottom: -3% !important;
  background: url("data:image/svg+xml;base64,{data}") center / contain no-repeat;
}}
"""

def data_uri(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def slash(path):
    return path.replace("\\", "/")

def main():
    ap = argparse.ArgumentParser(description="Make a Fluidd custom.css"
                                 " with a theme's logo")
    ap.add_argument("logo", help="sidebar-logo.svg of the Mainsail theme")
    ap.add_argument("out", help="custom.css to write")
    ap.add_argument("--background", help="logo for the bottom right corner")
    ap.add_argument("--base", help="stylesheet to put first")
    args = ap.parse_args()
    css = ""
    if args.base:
        with open(args.base) as f:
            css = "/* From %s */\n%s\n\n" % (slash(args.base), f.read().strip())
    css += CSS.format(name=slash(args.logo), data=data_uri(args.logo))
    if args.background:
        css += BACKGROUND_CSS.format(name=slash(args.background),
                                     data=data_uri(args.background))
    with open(args.out, "w", newline="\n") as f:
        f.write(css)

if __name__ == "__main__":
    main()
