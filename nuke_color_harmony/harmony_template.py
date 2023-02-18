ADD_KNOB = "  addUserKnob {{41 color{constant_index} T Group{group_index}.Constant{constant_index}.color}}"

SINGLE_COLOR = """Constant {{
  inputs 0
  channels rgb
  color {{{red} {green} {blue} 1}}
  name Constant{constant_index}
  xpos {xpos}
  ypos -33
}}
Reformat {{
  type "to box"
  box_width {reformat_width}
  box_height {reformat_height}
  box_fixed true
  resize distort
  name Reformat{constant_index}
  xpos {xpos}
  ypos 67}}"""

GROUP = """Group {{
  inputs 0
  name Group{group_index}
  label {color_harmony}
  xpos {group_xpos}
  ypos 9
  postage_stamp true
  addUserKnob {{20 nuke_color_harmony}}
  addUserKnob {{26 harmony l  {color_harmony} }}
{add_user_knobs_to_script} }}
{add_colors_to_script}ContactSheet {{
  inputs 5
  width {cs_width}
  height {cs_height}
  rows 1
  columns {color_amount}
  gap 20
  center true
  name ContactSheet1
  ypos 267
}}
Output {{
  name Output1
}}
end_group"""

MAIN_SCRIPT = """set cut_paste_input [stack 0]
version {nuke_version_string}
{add_groups_to_script}
"""
