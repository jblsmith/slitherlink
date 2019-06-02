from PIL import Image, ImageDraw, ImageFont
import numpy as np
import re

class Grid:
	
	def __init__(self, dims=[4,4]):
		self.n_cells = dims
		self.n_ticks = (dims[0]+1,dims[1]+1)
		self.hlines = np.zeros(dims[0],dims[1]+1)
		self.vlines = np.zeros(dims[1],dims[0]+1)
		self.verts = np.zeros(self.n_ticks)
		self.cells = np.zeros(self.n_cells)
		self.grid = "."*np.prod(self.n_cells)
		self.image_filename = "tmp.png"
		self.draw_grid_scale = 30
	
	def set_grid(self, numbers):
		numbers = re.sub(" ","",numbers)
		if len(numbers) == np.prod(self.n_cells):
			self.grid = numbers
		else:
			print "No action; did not enter valid grid size."
	
	def set_lines(self, lines):
		lines = re.sub(" ","",lines)
		print self.n_cells[0]*self.n_ticks[1] + self.n_cells[1]*self.n_ticks[0]
		if len(lines) == self.n_cells[0]*self.n_ticks[1] + self.n_cells[1]*self.n_ticks[0]:
			self.lines = lines
		else:
			print "No action; number of lines incorrect."
	
	def lines_as_HV(self):
		assignments = ([0]*self.n_cells[0] + [1]*self.n_ticks[0])*self.n_cells[1] + [0]*self.n_cells[0]
		self.hlines = [self.lines[i] for i in range(len(self.lines)) if assignments[i]==0]
		self.vlines = [self.lines[i] for i in range(len(self.lines)) if assignments[i]==1]
	
	def show_grid(self):
		k = self.draw_grid_scale
		x_off = k
		y_off = k
		im = Image.new('RGB',((self.n_ticks[0]+1)*k,(self.n_ticks[1]+1)*k), (255,255,255))
		d = ImageDraw.Draw(im)
		# Draw tick marks of grid
		for i in range(1,1+self.n_ticks[0]):
			for j in range(1,1+self.n_ticks[1]):
				d.line([i*k-2,j*k,i*k+2,j*k],fill="#aaa")
				d.line([i*k,j*k-2,i*k,j*k+2],fill="#aaa")
		# Draw numbers
		font = ImageFont.load_default()
		for i,x in enumerate(self.grid):
			if x!=".":
				i_x = i%self.n_cells[0]+1
				i_y = i/self.n_cells[0]+1
				tex_x = i_x*k+k/2-font.getsize(x)[0]/2
				tex_y = i_y*k+k/2-font.getsize(x)[1]/2
				d.text((tex_x, tex_y), x, font=font, fill="#000")
		# Draw lines
		self.lines_as_HV()
		for i,x in enumerate(self.hlines):
			if x=="-":
				i_x = (i%self.n_cells[0]+1)*k
				i_y = (i/self.n_cells[0]+1)*k
				d.line( [(i_x,i_y), (i_x +k,i_y)], fill="#000")
		for i,y in enumerate(self.vlines):
			if y=="-":
				i_x = (i%self.n_ticks[0]+1)*k
				i_y = (i/self.n_ticks[0]+1)*k
				d.line( [(i_x,i_y), (i_x,i_y+k)], fill="#000")
		del d
		# Save output
		im.save(self.image_filename)
	
	def reset_lines(self):
		

a = Grid()
a.set_grid(numbers="0..2 .30. .32. 1..3")
a.set_lines("..-- ..-.- .-.. .-..- .-.- ..--. .-.- .-..- ____")
a.show_grid()


# New plan:

# Represent every aspect of the grid:
# (In a 10x20 grid, c_row = cell_row runs from 1 to 10; v_row = vertex_row runs from 1 to 11.)
								Potential values:
								Given:		Deduced:	Unknown:
- vline(c_row, v_column)		-			1,-1		0	(line vs blank)
- hline(v_row, c_column)		-			1,-1		0	(line vs blank)
- vertex(v_row, v_column)		-			1,-1		0	(visited vs unvisited)
- cell(c_row, c_column)			-			1,-1		0	(visited vs unvisited)?
- number(c_row, c_column)		0,1,2,3		0,1,2,3		0
- shade(c_row, c_column)		-			1,-1		0	(inside vs outside)
- snake(index, endpoints)		-			1,2,3,...	-	(line name)

# But how to keep track of and enforce the constraint that the full grid contain a single loop?
# We could label every line segment's endpoints, and ensure that no two same-named endpoints can meet, unless it's the end of the grid.

Operations:
- Implement plain constraints:
	- Paint all lines around 0 cell as -1
	- Draw any lines around cells if number of lines left to be drawn = number of lines available
	- If line enters and exits vertex, other lines from that vertex are invalid
- Extend slitherlink:
	- If line entering vertex has only one option out, draw it
- Deductions:
	- If 3 lines entering vertex are invalid, 4th must be invalid too.
	- If proposed line creates closed snake, line is invalid.
- Standard situations as starting points:
	- 0 next to 3 --> _|–|_
	- 3 next to 3 --> | | |
	- 2 or 3 in a corner
	- etc.
- Reserve snake numbers:
	- Every 1 or 3 cell gets a unique snake number
	- Every 2 cell gets two unique numbers
	- Whenever two snakes joined, overwrite with the lesser snake number



from PIL import Image, ImageDraw, ImageFont
import numpy as np
import re
import os

class Grid:
	def __init__(self, dims=[4,4], name="grid"):
		# Set up all variables
		n_rows, n_cols = dims
		self.n_rows = n_rows
		self.n_cols = n_cols
		# self.vline[i,j] = the line between cells j and j+1 in row i
		# self.hline[i,j] = the line between cells i and i+1 in row j
		# self.vertex[i,j] = the point between rows i and i+1 and columns j and j+1
		self.vline = np.zeros((n_rows, n_cols+1)).astype(int)
		self.hline = np.zeros((n_rows+1, n_cols)).astype(int)
		self.vertex = np.zeros((4, n_rows+1, n_cols+1)).astype(int)-1
		self.cell = np.zeros(dims).astype(int)
		self.number = np.zeros(dims).astype(int)-1
		self.shade = np.zeros(dims).astype(int)
		self.image_filename = name+".png"
		self.draw_grid_scale = 30
		self.font_path = "/Library/Fonts/Courier New.ttf"
	def set_grid(self, number_array):
		# Define an input grid
		if type(number_array) is str:
			number_array = self.numbers_str_to_array(number_array)
		assert number_array.shape == self.number.shape, "Shape of grid and input to set_grid do not match."
		assert np.min(number_array)>=-1, "Values less than -1 detected."
		assert np.max(number_array)<=3, "Values greater than 3 detected."
		self.number = number_array
		n_snakes = np.sum(number_array==1) + 2*np.sum(number_array==2) + np.sum(number_array==3)
		self.snake = np.zeros((n_snakes, 1, 1))
		# Set NESW vertex impossibilities: Nothing can come from NORTH in top row, from EAST in right row, etc.
		print("Setting edge vertex constraints...")
		self.vertex[0,0,:] = -2
		self.vertex[1,:,-1] = -2
		self.vertex[2,-1,:] = -2
		self.vertex[3,:,0] = -2
	def set_lines(self, hline_array, vline_array):
		# Define line placements
		if type(hline_array) is str:
			hline_array = self.lines_str_to_array(hline_array)
		if type(vline_array) is str:
			vline_array = self.lines_str_to_array(vline_array).transpose()
		assert hline_array.shape == self.hline.shape, "hline_array has incorrect shape, should be %r" % self.hline.shape
		assert vline_array.shape == self.vline.shape, "vline_array has incorrect shape, should be %r" % self.vline.shape
		assert (np.min(hline_array)>=-1) & (np.max(hline_array)<=1) & (np.min(vline_array)>=-1) & (np.max(vline_array)<=1), "Some value in hline_array or vline_array is not between -1 and 3."
		# assert np.max(hline_array)<=1
		# assert np.min(vline_array)>=-1
		# assert np.max(vline_array)<=1
		self.vline = vline_array
		self.hline = hline_array
	def numbers_str_to_array(self, number_string):
		rows = number_string.split(" ")
		assert self.n_cols == len(rows[0])
		assert self.n_rows == len(rows)
		number_array = np.zeros_like(self.number)-1
		for i,row in enumerate(rows):
			for j,char in enumerate(row):
				if char in ["0","1","2","3"]:
					number_array[i,j] = int(char)
		return number_array
	def lines_str_to_array(self, line_string):
		segs = line_string.split(" ")
		n_segs = len(segs)
		seg_n = len(segs[0])
		line_array = np.zeros((n_segs,seg_n)).astype(int)
		line_dict = {".":-1, "-":1, "_":0}
		for i,row in enumerate(segs):
			for j,char in enumerate(row):
				line_array[i,j] = line_dict[char]
		return line_array
	def print_grid(self, include_lines=True, include_numbers=True, include_xs=True, include_ticks=True):
		# Print grid, with or without lines or numbers
		k = self.draw_grid_scale
		x_off = k
		y_off = k
		im = Image.new('RGB',((self.n_cols+2)*k, (self.n_rows+2)*k), (255,255,255))
		d = ImageDraw.Draw(im)
		# Draw tick marks of grid
		tw = 2  # tick (half)-width
		if include_ticks:
			for i in range(1,self.n_cols+2):
				for j in range(1,self.n_rows+2):
					d.line([i*k-tw,j*k,i*k+tw,j*k],fill="#aaa")
					d.line([i*k,j*k-tw,i*k,j*k+tw],fill="#aaa")
		# Draw numbers
		if include_numbers:
			# font = ImageFont.load_default()
			# font = ImageFont.truetype("sans-serif.ttf", k)
			font = ImageFont.truetype(self.font_path,size=int(k/2))
			for i,j in zip(*np.where(self.number>-1)):
				x = self.number[i,j].astype(str)
				# tex_x = j*k+k/2-font.getsize(x)[0]/2
				# tex_y = i*k+k/2-font.getsize(x)[1]/2
				tex_x = (j+1.5)*k - font.getsize(x)[0]/2.0 # + 1
				tex_y = (i+1.5)*k - font.getsize(x)[1]/2.0 # + 1
				d.text((tex_x, tex_y), x, font=font, fill="#000")
				# print(x, tex_x, tex_y)
		# Draw lines
		if include_lines:
			for i,j in zip(*np.where(self.hline==1)):
				x = (j+1)*k
				y = (i+1)*k
				d.line( [(x,y), (x+k,y)], fill="#000")
			for i,j in zip(*np.where(self.vline==1)):
				x = (j+1)*k
				y = (i+1)*k
				d.line( [(x,y), (x,y+k)], fill="#000")
		# Draw invalid lines
		if include_xs:
			tw = k/10  # tick (half)-width
			for i,j in zip(*np.where(self.hline==-1)):
				x = (j+1)*k + k/2
				y = (i+1)*k
				d.line([x-tw,y-tw,x+tw,y+tw],fill="#aaa")
				d.line([x-tw,y+tw,x+tw,y-tw],fill="#aaa")
			for i,j in zip(*np.where(self.vline==-1)):
				x = (j+1)*k
				y = (i+1)*k + k/2
				d.line([x-tw,y-tw,x+tw,y+tw],fill="#aaa")
				d.line([x-tw,y+tw,x+tw,y-tw],fill="#aaa")
		del d
		im.save(self.image_filename)
	# def fill_cells(self):
	# 	# For every cell: can we immediately deduce where to draw lines around it?
	# def extend_lines(self):
	# 	# For each line: can we extend it in obvious way?
	def update_vertices_from_lines(self):
		# For every line that exists:
		# 	Vertex-1 must reflect it out
		# 	Vertex-2 must reflect it in
		# For every line that cannot exist:
		# 	Do the same
		#
		# Do hlines first, then vlines:
		for row_i in range(self.hline.shape[0]):
			h_ones = np.where(self.hline[row_i,:]==1)[0]
			h_minus_ones = np.where(self.hline[row_i,:]==-1)[0]
			for col_j in h_ones:
				self.vertex[1,row_i,col_j]=1
				self.vertex[3,row_i,col_j+1]=1
			for col_j in h_minus_ones:
				self.vertex[1,row_i,col_j]=-1
				self.vertex[3,row_i,col_j+1]=-1
		for col_i in range(self.vline.shape[1]):
			v_ones = np.where(self.vline[:,col_i]==1)[0]
			v_minus_ones = np.where(self.vline[:,col_i]==-1)[0]
			for row_j in v_ones:
				self.vertex[2,row_j,col_i]=1
				self.vertex[0,row_j+1,col_i]=1
			for row_j in v_minus_ones:
				self.vertex[2,row_j,col_i]=-1
				self.vertex[0,row_j+1,col_i]=-1
	def lines_around_cell(self, coords):
		y,x = coords
		top = self.hline[y,x]
		bottom = self.hline[y+1,x]
		left = self.vline[y,x]
		right = self.vline[y,x+1]
		trbl = np.array([top, right, bottom, left])
		return trbl
	def lines_into_vertex(self, coords):
		y,x = coords
		return self.vertex[:,y,x]
		# If the vertex is in the middle, it will have all lines from all 4 directions.
		if (0<y<self.n_rows) and (0<x<self.n_cols):	
			north = self.vline[y-1,x]
			south = self.vline[y,x]
			east = self.hline[y,x]
			west = self.hline[y,x-1]
			nesw = np.array([north, east, south, west])
			return nesw
		# elif (y==0)
	# def update_lines(self):
	# 	# Update line info based on other stuff (cells, vertices, shading)
	# 	for y,x in zip(*np.where(self.number>-1)):
	# 		trbl = self.lines_around_cell([y,x])
	# 		space_used = np.sum(trbl==1)
	# 		space_left = np.sum(trbl==0)
	# 		if (space_used == number):
	# 			# assign remaining spaces to be -1
	# 			# i.e., set any 0 to -1
	#




		
			



# number = self.number[y,x]
#
# 		for y,x in zip(*np.where(self.number>-1)):
# 			top = self.hline[]
# 	# def update_vertices(self):
# 	# 	# Update vertex info
# 	# def update_cells(self):
# 	# 	# Update cell info
# 	# def update_shading(self):
# 	# 	# Update shade info
# 	# def merge_snakes(self, snake1, snake2):
# 	# 	# Merge two snakes
#
#
# g = Grid()
# g.set_grid("0..2 .30. .32. 1..3")
# g.set_lines("..-- .-.. .-.- .-.- .---", "..-.- .-..- ..--. .-..-")
# g.print_grid()

# Wikipedia grid
g = Grid(dims=[6,6], name="wikipedia")
g.set_grid("....0. 33..1. ..12.. ..20.. .1..11 .2....")
g.set_lines("---... .-...- -..-.. ....-. ..-... ---.-. ----.-",
			"--...- .-.... .---.. --..-. ..-..- .--..- .-----")
g.update_vertices_from_lines()
g.print_grid()

g = Grid(dims=[10,6], name='example')
g.set_grid("012321 123210 ...2.. ..2... ...2.. ..2... ...2.. ..2... 121202 202121")
# g.set_lines("..-- .-.. .-.- .-.- .---", "..-.- .-..- ..--. .-..-")
g.print_grid()








print_test:
a = Image.new('RGB',(50,50), (255,255,255))
b = ImageDraw.Draw(a)
font = ImageFont.load_default()
b.text((10,10), "ABCD", font=font, fill="#000")
a.save("tmp.jpg")





