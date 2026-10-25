#!/usr/bin/env python3
# Writes a Fluidd custom.css that shows a theme's sidebar-logo.svg in the
# top bar instead of Fluidd's logo. Fluidd reads only custom.css and
# background.* from .fluidd-theme, so the logo goes in as a data URI.
#
#   python3 tools/fluidd_logo_css.py themes/kiln-ad5x/sidebar-logo.svg \
#       fluidd-themes/kiln-ad5x/custom.css
import base64
import sys

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

def main():
    if len(sys.argv) != 3:
        sys.exit("usage: fluidd_logo_css.py <sidebar-logo.svg> <custom.css>")
    src, out = sys.argv[1:]
    with open(src, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    with open(out, "w", newline="\n") as f:
        f.write(CSS.format(name=src.replace("\\", "/"), data=data))

if __name__ == "__main__":
    main()
