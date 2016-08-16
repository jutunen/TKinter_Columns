# settings file for tkinter-columns.py
# ALL NUMERICAL VALUES MUST BE INTEGERS!

# difficulty level is the bar animation rate in milliseconds
# setting the final level to same or bigger than the initial level disables level raising:
difficulty_level_raise_interval = 60 # seconds
initial_difficulty_level = 27 # the bigger the easier
final_difficulty_level = 7 # the smaller the harder, must be bigger than zero

# block dimensions in pixels, height and width:
block_h = 30
block_w = 30

# block_h and block_w must be divisible by two, do not modify following 4 lines:
if(block_h % 2 != 0):
  block_h += 1
if(block_w % 2 != 0):
  block_w += 1

blocks_in_bar = 3

# number of consecutive blocks needed for vanishing, must be bigger than one:
critical_mass = 3 

# pit dimensions in pixels, height and width
# do not remove variables, modify last integer only:
pit_h = block_h * blocks_in_bar * 7
pit_w = block_w * 9

# available block colors:
block_colors = ["yellow", "#ff5050", "cyan", "green", "#bfbfbf"]

# number of block colors in use:
block_colors_in_use = 5

# control keys configuration:
move_left = '<Left>' # left arrow
move_right = '<Right>' # right arrow
cycle_colors_up = '<Up>' # up arrow
cycle_colors_down = '<KP_0>' # 0 on the keypad
landing_speed_up = '<Down>' # down arrow 
pause_key = '<Pause>'

# For a more complete reference on TKinter key names visit:
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/key-names.html