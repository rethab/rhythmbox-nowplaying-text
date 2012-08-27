# Mode: python; coding: utf-8; tab-width: 2;
# 
# Copyright (C) 2009 - Kyle Florence
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

# this is not the original version of this file.  output has been hacked up.
# writes to fifo instead of file.

import os
from gi.repository import GObject, RB, Peas

class NowPlayingTextPlugin (GObject.Object, Peas.Activatable):

  MAXLEN = 50

  object = GObject.property(type=GObject.Object)

  def __init__(self):
    super(NowPlayingTextPlugin, self).__init__()

  # What to do on activation
  def do_activate(self):
    print "NowPlayingTextPlugin activated"
    self.shell = self.object
    self.db = self.shell.props.db
    self.current_entry = None
    self.output_file = os.path.expanduser('~') + "/.rhythmbox.out"

    file = os.open(self.output_file, os.O_RDWR)
    os.write(file, " \n") 
    os.close(file)

    # Reference the shell player
    sp = self.shell.props.shell_player

    # bind to "playing-changed" signal
    self.pc_id = sp.connect(
      'playing-changed',
      self.playing_changed
    )
    
    # bind to "playing-song-changed" signal
    self.psc_id = sp.connect(
      'playing-song-changed',
      self.playing_song_changed
    )
    
    # bind to "playing-song-property-changed" signal
    self.pspc_id = sp.connect(
      'playing-song-property-changed',
      self.playing_song_property_changed
    )

    # Set current entry if player is playing
    if sp.get_playing(): self.set_entry(sp.get_playing_entry())
  
  # What to do on deactivation
  def do_deactivate(self): 
    print "NowPlayingTextPlugin deactivated"
    # Disconnect signals
    sp = self.shell.props.shell_player
    sp.disconnect(self.psc_id)
    sp.disconnect(self.pc_id)
    sp.disconnect(self.pspc_id)
    
    file = os.open(self.output_file, os.O_RDWR)
    os.write(file, " \n") 
    os.close(file)

    # Remove references
    del self.db
    del self.shell
    del self.current_entry
    del self.output_file

  # Player was stopped or started
  def playing_changed(self, sp, playing):
    if playing: self.set_entry(sp.get_playing_entry())
    else: self.current_entry = None

  # The playing song has changed
  def playing_song_changed(self, sp, entry):
    if sp.get_playing(): self.set_entry(entry)

  # A property of the playing song has changed
  def playing_song_property_changed(self, sp, uri, property, old, new):
    if sp.get_playing(): self.get_songinfo_from_entry()

  # Sets our current RythmDB entry
  def set_entry(self, entry):
    if entry == self.current_entry: return
    if entry is None: return

    self.current_entry = entry

    # Extract songinfo from the current entry
    self.get_songinfo_from_entry()

  # Gets current songinfo from a rhythmdb entry
  def get_songinfo_from_entry(self):
    # Set properties list
    properties = {
      "title":RB.RhythmDBPropType.TITLE,
      "genre":RB.RhythmDBPropType.GENRE,
      "artist":RB.RhythmDBPropType.ARTIST,
      "album":RB.RhythmDBPropType.ALBUM
    }

    # Get song info from the current rhythmdb entry
    properties = dict(
      (k, self.current_entry.get_string(v))
      for k, v in properties.items()
    )

    # what media type? (a radio stream may use different
    # fields to display information)
    mtype = self.current_entry.get_string(RB.RhythmDBPropType.MEDIA_TYPE)
    
    # Pass songinfo properties to text write function
    self.write_from_songinfo(properties, mtype)
    
  # Write songinfo to text file
  def write_from_songinfo(self, properties, mtype):
    output = self.format_output(properties, mtype)

    # Write to file
    file = os.open(self.output_file, os.O_RDWR)
    os.write(file, output[0:self.MAXLEN]+"\n") 
    os.close(file)

  def format_output(self, properties, mtype):
    if mtype == "application/octet-stream":
      return properties['title'] + " (" + ".." + ")"
    else:
      return properties['artist'] + " - " + properties['title'] 
