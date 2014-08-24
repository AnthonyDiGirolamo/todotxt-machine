#!/usr/bin/env python
# coding=utf-8

import os
import sys

# Import the correct version of configparser
if sys.version_info[0] >= 3:
    import configparser
    config_parser_module = configparser
elif sys.version_info[0] < 3:
    import ConfigParser
    config_parser_module = ConfigParser

class ColorScheme:

    def __init__(self, name, user_config):
        self.built_in_colors_directory = os.path.realpath(os.path.expanduser(os.path.dirname(__file__) + '/colors'))
        self.user_config = user_config
        self.load_colors(name)

    def load_colors(self, name):
        self.colors = {}
        self.focus_map = {}
        self.dialog_focus_map = {}
        colorscheme_section = "colorscheme-{0}".format(name)

        # Use user defined theme in the user_config if it exists
        if self.user_config.has_section(colorscheme_section):
            self.colors = dict( self.user_config.items(colorscheme_section) )
        else:
            # Try to load a built in theme
            cfg = config_parser_module.ConfigParser()
            if name in os.listdir(self.built_in_colors_directory):
                cfg.read(self.built_in_colors_directory + "/" + name)
            # Load default theme
            else:
                cfg.read(self.built_in_colors_directory + "/default")
                colorscheme_section = "colorscheme-default"
            if cfg.has_section(colorscheme_section):
                self.colors = dict( cfg.items(colorscheme_section) )

        # Split foreground and background values
        for key, value in self.colors.items():
            color_strings = value.split(',')
            if len(color_strings) == 1:
                color_strings.append('')
            self.colors[key] = {'fg': color_strings[0], 'bg': color_strings[1]}

        # Create Selected attributes using the selected_background_color
        selected_background_color = self.colors['selected']['bg']
        dialog_color = self.colors['dialog_color']['bg']
        # dialog_button_color = self.colors['dialog_button_color']['bg']
        for key, value in list(self.colors.items()):
            if key not in ['selected', 'dialog_color', 'dialog_button_color']:
                self.colors[key+'_selected'] = {'fg': self.colors[key]['fg'], 'bg': selected_background_color}
                self.colors[key+'_dialog_color'] = {'fg': self.colors[key]['fg'], 'bg': dialog_color}
                # self.colors[key+'_dialog_button_color'] = {'fg': self.colors[key]['fg'], 'bg': dialog_button_color}
                self.focus_map[key] = key + '_selected'
                self.dialog_focus_map[key] = key + '_dialog_color'
                # self.dialog_focus_map[key] = key + '_dialog_button_color'
