# Now Playing Text - Rhythmbox plugin - 0.1

Rhythmbox plugin that prints artist, song, and rating to a text file.  Forked from rhythmbox-nowplaying-xml

## Installation

First, open the terminal and issue the following commands:

    mkdir -p ~/.gnome2/rhythmbox/plugins
    cd ~/.gnome2/rhythmbox/plugins
    git@github.com:sagotsky/rhythmbox-nowplaying-text.git

Then enable the plugin within Rhythmbox by going to "Edit", selecting "Plugins"
and then checking the "Now Playing Text" plugin.

## Xmobar

To use this with xmobar (which is what I forked the xml version for), create a fifo:
  mkfifo ~/.rhythmbox.out
Add a PipeReader to your .xmobarrc
  , Run PipeReader    "/home/sagotsky/.rhythmbox.out" "music"
And add %music% to your template

