from tkinter import *
import random, os, math, time

try:
  from game_settings import *
except ImportError:
  print("Importing settings file failed!")

try:
  difficulty_level_raise_interval
except NameError:
  difficulty_level_raise_interval = 60 # seconds

try:
  initial_difficulty_level
except NameError:
  initial_difficulty_level = 27 # the bigger the easier
  
try:
  final_difficulty_level
except NameError:
  final_difficulty_level = 7 # the smaller the harder

# block dimensions in pixels, height and width:
try:
  block_h
except NameError:
  block_h = 30
  
try:
  block_w
except NameError:
  block_w = 30

# block_h and block_w must be divisible by two:
if(block_h % 2 != 0):
  block_h += 1
if(block_w % 2 != 0):
  block_w += 1

try:
  blocks_in_bar
except NameError:
  blocks_in_bar = 3

# number of consecutive blocks needed for vanishing, must be bigger than one:
try:
  critical_mass
except NameError:
  critical_mass = 3

# pit dimensions in pixels, height and width:
try:
  pit_h
except NameError:
  pit_h = block_h * blocks_in_bar * 7 # do not remove variables, modify only the last integer

try:
  pit_w
except NameError:
  pit_w = block_w * 9 # do not remove variable, modify only the last integer

# available block colors:
try:
  block_colors
except NameError:  
  block_colors = ["yellow", "#ff5050", "cyan", "green", "#bfbfbf"]

# number of block colors in use:  
try:
  block_colors_in_use
except NameError:
  block_colors_in_use = 5
  
# control keys configuration:
try:
  move_left
except NameError:
  move_left = '<Left>' # left arrow
  
try:
  move_right
except NameError:  
  move_right = '<Right>' # right arrow

try:
  cycle_colors_up
except NameError:  
  cycle_colors_up = '<Up>' # up arrow
  
try:
  cycle_colors_down
except NameError:  
  cycle_colors_down = '<KP_0>' # 0 on the keypad
  
try:
  landing_speed_up
except NameError:  
  landing_speed_up = '<Down>' # down arrow

try:
  pause_key
except NameError:    
  pause_key = '<Pause>'  

#convert interval to milliseconds  
difficulty_level_raise_interval = difficulty_level_raise_interval * 1000

#critical mass must be bigger than one:
if critical_mass < 2:
  critical_mass = 2

#final difficulty level must be bigger than zero:
if final_difficulty_level < 1:
  final_difficulty_level = 1

if block_colors_in_use < 1 or block_colors_in_use > len(block_colors):
  raise ValueError('block_colors_in_use is too small or too big!')

class Bar:
   
   def __init__(self, colors = [0,1,2]): 
     shift_x = (math.floor((pit_w / block_w) / 2)) * block_w
     self.rects = []
     self.colors = colors
     for i in range(len(self.colors)):
       self.rects.append(canvas.create_rectangle(0 + shift_x, i * block_h, block_w + shift_x, block_h + i * block_h, fill=map_color(self.colors[i])))
     
   def move(self, x, y):
     for rect in self.rects:
       canvas.move(rect, x, y)
     
   def cycle_colors(self,step):
     self.colors = self.colors[-step:] + self.colors[:-step]
     self.unpause_colors()
     
   def unpause_colors(self):
     for i in range(len(self.rects)):
       canvas.itemconfig(self.rects[i], fill=map_color(self.colors[i]))
     
   def pause_colors(self):
     for rect in self.rects:
       canvas.itemconfig(rect, fill="white")
     
   def get_height(self):
     return len(self.rects) * block_h
    
   def get_coords(self):
     return canvas.coords(self.rects[0])
    
   def get_color(self,index):
     return self.colors[index]

   def get_id(self,index):
     return self.rects[index]
      
   def get_block(self,index):
     return Block(self.colors[index], self.rects[index], self.column, self.row + len(self.rects) - 1 - index)
    
   def set_column(self,column):
     self.column = column
     
   def set_row(self,row):
     self.row = row

class Block:
  
  def __init__(self, color, id, column, row): 
    self.color = color
    self.id = id
    self.column = column
    self.row = row
    
  def __repr__( self ): #this is for debugging purposes
    return "c" + str(self.color) + "_" + str(self.id) + "_" + str(self.column) + "_r" + str(self.row)  

class Scheduler:
  
  def __init__(self):
    self.scheduler_1 = False
    self.scheduler_2 = False
    self.scheduler_3 = False
    self.scheduler_4 = False
    self.sched_4_id = None
  
  def stop_game_speed_scheduler(self):
    self.scheduler_4 = False
    Bar.vertical_anim_rate_cache += 1 #because this will be decreased by one when game speed scheduler is started
    self.game_speed_scheduler()
    
  def start_game_speed_scheduler(self):
    self.scheduler_4 = True
    self.game_speed_scheduler(int(difficulty_level_raise_interval / 2))
  
  def start_all(self):
    self.start_stop(True)
    
  def stop_all(self):
    self.start_stop(False)    
  
  def start_stop(self,boolean):
    self.scheduler_1 = boolean
    self.scheduler_2 = boolean
    self.scheduler_3 = boolean
    self.scheduler_4 = boolean
    
    self.animate_bar_vertical()    
    self.animate_bar_horizontal()    
    self.speed_burst_brake()    
    self.game_speed_scheduler()
      
  def is_running(self):
    if self.scheduler_1 or self.scheduler_2 or self.scheduler_3 or self.scheduler_4:
      return True
    else:
      return False
 
  def animate_bar_vertical(self):
    if not self.scheduler_1:
      return    
    draw_one_frame_vert()
    root.after(Bar.vertical_anim_rate, self.animate_bar_vertical)
    
  def animate_bar_horizontal(self):
    if not self.scheduler_2: 
      return    
    draw_one_frame_hori()
    root.after(Bar.horizontal_anim_rate, self.animate_bar_horizontal)    
    
  def speed_burst_brake(self):
    if not self.scheduler_3:
      return    
    if(Bar.speed > Bar.speed_cache):
      Bar.speed -= 2
    root.after(Bar.speed_burst_rate, self.speed_burst_brake)
  
  # increases level of difficulty per interval
  def game_speed_scheduler(self,interval = difficulty_level_raise_interval): 
    if not self.scheduler_4:
      # following is needed because start_game_caller interval won't cover difficulty_level_raise_interval:
      root.after_cancel(self.sched_4_id) 
      return    
    if(Bar.vertical_anim_rate_cache > final_difficulty_level):
      Bar.vertical_anim_rate_cache -= 1
      Bar.vertical_anim_rate = Bar.vertical_anim_rate_cache
    self.sched_4_id = root.after(interval, self.game_speed_scheduler)
    
  def start_game_caller(self):
    # here the interval must be big enough to cover all schedulers except game speed scheduler:
    root.after(100, start_game) 

def pause_game():
  global game_paused
  
  if bar:
    if not(game_paused):
      game_paused = True
      scheduler.stop_game_speed_scheduler()
      Bar.speed = 0
      root.bind('<Left>', ignoreKey)
      root.bind('<Right>', ignoreKey)
      root.bind('<Up>', ignoreKey)
      root.bind('<Down>', ignoreKey)
      pause_block_colors()
      bar.pause_colors()
      pause_btn_str.set("Resume")
    else:
      game_paused = False
      scheduler.start_game_speed_scheduler()
      unpause_block_colors()
      bar.unpause_colors()
      bindKeys()
      Bar.speed = Bar.speed_cache
      pause_btn_str.set("Pause")
    
def pause_block_colors():
  for i in range(len(block_array_2d)):
    for ii in range(len(block_array_2d[i])):
      canvas.itemconfig(block_array_2d[i][ii].id, fill="white")

def unpause_block_colors():
  for i in range(len(block_array_2d)):
    for ii in range(len(block_array_2d[i])):
      canvas.itemconfig(block_array_2d[i][ii].id, fill=map_color(block_array_2d[i][ii].color))
    
def get_random_color():
  randomi = random.randrange(0,block_colors_in_use)
  return randomi

def map_color(color):
  return block_colors[color]
  
def start_game():
  
  global points
  global block_array_2d
  global fill_levels
  global to_be_destroyed
  global to_be_landed
  global bar
  global game_paused
  
  if scheduler.is_running():
    scheduler.stop_all()
    scheduler.start_game_caller()
    return
  
  block_array_2d = []
  fill_levels = []
  to_be_destroyed = []
  to_be_landed = []
  
  del to_be_landed[:]
  del to_be_destroyed[:]

  for i in range(grid_w):
    block_array_2d.append([])
    fill_levels.append(0)  
  
  canvas.delete("all")
  bar = None
  score.set("score:\n0")
  game_paused = False
  pause_btn_str.set("Pause")
  
  Bar.speed_cache = 1
  Bar.speed = Bar.speed_cache  
  Bar.vertical_anim_rate_cache = initial_difficulty_level
  Bar.vertical_anim_rate = Bar.vertical_anim_rate_cache
  points = 0  
  
  scheduler.start_all()

def new_bar():
  global bar
  Bar.speed = Bar.speed_cache
  
  colors_list = []
  for _ in range(blocks_in_bar):
    colors_list.append(get_random_color())
  
  bar = Bar(colors_list)
  #if(random.choice([True, False])):
  #  bar = Bar([1,2,3])
  #else:
  #  bar = Bar([1,4,3])
  
def landed(coords):
  global fill_levels
  column = int(round(coords[0] / block_w)) #column index
  if(coords[1] + Bar.speed >= pit_h - (fill_levels[column] * block_h + bar.get_height())):
    fill_levels[column] += int(bar.get_height()/block_h)
    vertical_pixel_offset = coords[1] - ( pit_h - fill_levels[column] * block_h)
    bar.move(0, -vertical_pixel_offset)
    return column * block_w
  else:
    return -1
  
def shifted(coords): #check if bar is horizontally shifted on a "column track"
  if(coords[0] % block_w == 0):
    return True #the bar is on the track
  else:
    return False #the bar is somewhere between the tracks

def draw_one_frame_hori():
  if bar:
    coords = bar.get_coords()
    if not coords:
      return
    if shifted(coords):
      return False
    else:
      bar.move(Bar.horizontal_move_step * Bar.direction , 0)
      return True

def draw_one_frame_vert():
  
  global to_be_destroyed
  global to_be_landed
  global points
  
  if game_paused:
    return

  if len(to_be_landed) > 0:
    redraw_all_blocks()
    update_fill_levels()
    del to_be_landed[:]
  
  elif len(to_be_destroyed) > 0:
    Bar.vertical_anim_rate = 300 #make destroying and landing more visible by slowing anim rate
    to_be_landed = get_blocks_to_be_landed(to_be_destroyed)
    delete_blocks(to_be_destroyed)
    update_fill_levels()
    points += len(to_be_destroyed)
    points_str = "score:" + "\n" + str(points)
    score.set(points_str)
    del to_be_destroyed[:]
  
  elif bar:
    new_x = landed(bar.get_coords())
    if new_x > -1:
      erotus = int(new_x - bar.get_coords()[0])
      bar.move(erotus , 0)
      column = int(round(bar.get_coords()[0] / block_w))
      bar.set_column(column)
      lowest_row = int(fill_levels[column] - bar.get_height() / block_h)
      bar.set_row(lowest_row) #pudonneen palkin alimmaisen palikan rivi
      
      for i in range(blocks_in_bar):
        block_array_2d[column].append(bar.get_block(blocks_in_bar - 1 - i))

      if fill_levels[column] > (pit_h / block_h):
        game_over()
        scheduler.stop_all()
        return
        
    else:
      if(bar.get_coords()[1] < 20):
        Bar.speed = Bar.speed_cache #disable speed burst for the range of first 20 pixels
      bar.move(0, Bar.speed)
      return
      
  to_be_destroyed = get_blocks_to_be_destroyed(block_array_2d)
  
  if len(to_be_landed) == 0 and len(to_be_destroyed) == 0:
    Bar.vertical_anim_rate = Bar.vertical_anim_rate_cache #return to normal anim rate after slow anim rate
    new_bar()
    
def game_over():
  x = int(pit_w / 2)
  y = int(pit_h / 2)
  font_size = int(pit_w / 5)
  text_id = canvas.create_text(x, y, font=("Arial",font_size,"bold"), fill="blue",text="GAME\nOVER")
  text_id_2 = canvas.create_text(x, y, font=("Arial",font_size - 5,"bold"), fill="white",text="GAME\nOVER")
    
#def debug_print():
#  for i in range(len(block_array_2d)):
#    print("\n")
#    for ii in range(len(block_array_2d[i])):
#      print(block_array_2d[i][ii], end=" ")
      
def redraw_all_blocks(): #re-draw and re-organize the grid
  
  for i in range(len(block_array_2d)):
    for ii in range(len(block_array_2d[i])):
      canvas.delete(block_array_2d[i][ii].id)
      
  for i in range(len(block_array_2d)): #grid_w
    for ii in range(len(block_array_2d[i])):
      canvas.delete(block_array_2d[i][ii].id) 
      block_array_2d[i][ii].column = i 
      block_array_2d[i][ii].row = ii
      x = i * block_w
      y = pit_h - ((ii + 1) * block_h)
      block_array_2d[i][ii].id = canvas.create_rectangle(x, y, x + block_w, y + block_h, fill=map_color(block_array_2d[i][ii].color))
      
def delete_blocks(lista):
  for i in range(len(lista)):
    canvas.delete(lista[i].id)
    block_array_2d[lista[i].column].remove(lista[i])
    
def update_fill_levels():
  for i in range(grid_w):
    fill_levels[i] = len(block_array_2d[i])   
    
def get_blocks_to_be_landed(lista):
  
  column = 0
  highest = 0
  lowest_list = [] # lowest block to be destroyed per column
  i = 0
  store = []
  global fill_levels
  blocks_per_column_max = 1000 # grid_h should not exceed this
  
  if( len(lista) == 0):
    return None
  
  for i in range(grid_w):
    lowest_list.append(blocks_per_column_max)
  
  for i in range(len(lista)):
    if(lista[i].row < lowest_list[lista[i].column]):
      lowest_list[lista[i].column] = lista[i].row

  for i in range(len(lowest_list)):
    if(lowest_list[i] < blocks_per_column_max):
      # extending store with lowest block to be destroyed and all blocks above it:
      store.extend(block_array_2d[i][(lowest_list[i] + 1):]) 
      
  # now store contains both blocks to be destroyed and blocks to be landed
  # removing blocks to be destroyed from store:
  new_store = [x for x in store if x not in lista]
                                  
  return new_store
  
def get_blocks_to_be_destroyed(grid):
  
  store = []
  consecs = None
  
  # vertical checking:
  for i in range(len(grid)):
    consecs = return_consecutives(grid[i])
    if(consecs):
      store.extend(consecs)
    
  # horizontal checking:
  rotated_grid = rotate_grid(grid) #lets rotate the grid so that we can re-use return_consecutives() function
  for i in range(len(rotated_grid)):
    consecs = return_consecutives(rotated_grid[i])
    if(consecs):
      store.extend(consecs)        

  return list(set(store)) #remove duplicates

def rotate_grid(lista):
  
  new_grid = []
  no_objects_at_all = True
  
  for i in range(grid_h):
    new_grid.append([])
    no_objects_at_all = True
    for ii in range(len(lista)):
      try:
        if(lista[ii][i]):
          new_grid[i].append(lista[ii][i])
          no_objects_at_all = False
      except IndexError:
          new_grid[i].append(None)
    if(no_objects_at_all):
      break
    
  return new_grid
  
#return indexes of matching blocks (= n or more similarly coloured consecutive blocks)    
def return_consecutives(lista):
  global critical_mass #number of consecutive blocks needed in order for them to vanish
  
  first_block = None
  consecutives = 1 #count
  for i in range(len(lista) - 1):
    if( lista[i] == None or lista[i + 1] == None):
      if(consecutives < critical_mass):
        consecutives = 1
        first_block = None    
      else:
        return lista[first_block:(first_block + consecutives)]        
    elif( lista[i].color == lista[i + 1].color ):
      consecutives += 1
      if(consecutives == 2):
        first_block = i
    else:
      if(consecutives < critical_mass):
        consecutives = 1
        first_block = None
      else:
        return lista[first_block:(first_block + consecutives)]
      
  if not(consecutives < critical_mass):
    return lista[first_block:(first_block + consecutives)]
      
def initiate_bar_horizontal_shifting():
  
  if bar:
    coords = bar.get_coords()
    
    if(coords[0] == 0 and Bar.direction == -1): #detect left side edge
      return
    
    if(coords[0] == (pit_w - block_w) and Bar.direction == 1): #detect right side edge
      return    
    
    try:
      if(coords[1] + bar.get_height() < pit_h - ( (fill_levels[int(round(coords[0] / block_w)) + Bar.direction] )  * block_h) ): # check if there is room for horizontal shifting
        bar.move(Bar.horizontal_move_step * Bar.direction , 0)      
    except IndexError: #because right side edge detection above is not 100% reliable, fill_levels might get over indexed
      pass
    
def cycleBarColorsUp(e):
  if bar:
    bar.cycle_colors(-1)
    
def cycleBarColorsDown(e):
  if bar:
    bar.cycle_colors(1)    

def leftKey(e):
  Bar.direction = -1 #to left
  initiate_bar_horizontal_shifting()

def rightKey(e):
  Bar.direction = 1 #to right
  initiate_bar_horizontal_shifting()
  
def speedBurst(e):
  if(Bar.speed < 20):
    Bar.speed += 4

def ignoreKey(e):
  return

def call_pause(e):
  pause_game()

def bindKeys():
  root.bind(move_left, leftKey)
  root.bind(move_right, rightKey)
  root.bind(cycle_colors_up, cycleBarColorsUp)
  root.bind(cycle_colors_down, cycleBarColorsDown)
  root.bind(landing_speed_up, speedBurst)
  root.bind(pause_key, call_pause)
  
root = Tk()
root.title("TKinter Columns")
#os.system('xset r off')
bindKeys()
mainframe = Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

Button(mainframe, text="New game", command=start_game, font=("Arial",20), borderwidth=3).grid(column=0, row=0, sticky=(S,W), padx=10, pady=10)
pause_btn_str = StringVar()
Button(mainframe, textvariable=pause_btn_str, command=pause_game, font=("Arial",20), borderwidth=3).grid(column=0, row=0, sticky=(S,W), padx=10, pady=100)
pause_btn_str.set("Pause")

c_frame = Frame(mainframe)
c_frame.grid(column=1, row=0)
c_frame.columnconfigure(0, weight=1)
c_frame.rowconfigure(0, weight=1)
c_frame['borderwidth'] = 3
c_frame['relief'] = 'sunken'

canvas = Canvas(c_frame, width=pit_w, height=pit_h, bg="black")
canvas.grid(column=1, row=0, sticky=(N, W, E, S))
bar = None

score = StringVar()
label = Label(mainframe, textvariable=score, font=("Arial",20), anchor=E, justify=LEFT).grid(column=0, row=0, sticky=(N,W), padx=20, pady=10)
score.set("score:\n0")

# 2 dimensional array for Block objects, aka the grid:
block_array_2d = []

# block_array_2d dimensions:
grid_w = int(pit_w / block_w)
grid_h = int(pit_h / block_h)

fill_levels = []

to_be_destroyed = []
to_be_landed = []  

Bar.speed_cache = 1
Bar.speed = Bar.speed_cache
Bar.vertical_anim_rate_cache = initial_difficulty_level
Bar.vertical_anim_rate = Bar.vertical_anim_rate_cache
Bar.horizontal_anim_rate = 10
Bar.horizontal_move_step = 2 # tämän on mentävä tasan block_w:in sisään   
Bar.speed_burst_rate = 70 # speed burst braking interval

points = 0

game_paused = False
scheduler = Scheduler()
root.mainloop()
