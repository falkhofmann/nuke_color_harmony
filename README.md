# **nuke_color_harmony**

This tool prevides the ability to work with [color harmonies](https://en.wikipedia.org/wiki/Harmony_(color)) inside the application [Nuke](https://www.foundry.com/products/nuke-family/nuke) from [The Foundry](https://www.foundry.com/).


 ## Usage
 While the main purpose is to run it inside  Nuke, it is also possible to use it as a standalone application.
 Inside Nuke however it can be either a floating PySide panel or a registered widget which then can be stored within you regualr workspace/layout.

## Import
When finished adding harmonies to the store, those can be imported into nuke. The imported result will be group node(s) which containing several constant nodes to dislpay the various colors as colorbars.
In addition the acutal color valuees are exposed on grouplevel so it is possible to link them across the nukescript and, if desired, live edit these.

 ## Export
Currently three different export options are supported:
- as .nk file to disk
- as .csv file to disk
- into the clipboard
 ## Live Linking

The idea behin live linking is, to dynamically change the knob values while editing harmonies in the panel. This allows to reduce the steps to find a the desired colors while working with the group nodes withinn Nuke.
