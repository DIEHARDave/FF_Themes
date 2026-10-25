#!/usr/bin/env python3
# Writes a Fluidd custom.css that shows a theme's sidebar-logo.svg in the
# top bar instead of Fluidd's logo, and optionally another logo in place of
# the faint one in the page's bottom right corner. Fluidd reads only
# custom.css and background.* from .fluidd-theme, so the logos go in as
# data URIs.
#
#   python3 tools/fluidd_logo_css.py themes/kiln-ad5x/sidebar-logo.svg \
#       fluidd-themes/kiln-ad5x/custom.css [logos/kiln-os-icon-background.svg]
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

def main():
    if len(sys.argv) not in (3, 4):
        sys.exit("usage: fluidd_logo_css.py <sidebar-logo.svg> <custom.css>"
                 " [background-logo.svg]")
    src, out = sys.argv[1:3]
    css = CSS.format(name=src.replace("\\", "/"), data=data_uri(src))
    if len(sys.argv) == 4:
        bg = sys.argv[3]
        css += BACKGROUND_CSS.format(name=bg.replace("\\", "/"),
                                     data=data_uri(bg))
    with open(out, "w", newline="\n") as f:
        f.write(css)

if __name__ == "__main__":
    main()
