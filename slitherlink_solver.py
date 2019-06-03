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
import itertools

class Grid:
	def __init__(self, dims=[4,4], name="grid"):
		# Set up all variables
		n_rows, n_cols = dims
		self.n_rows = n_rows
		self.n_cols = n_cols
		self.vline = np.zeros((n_rows, n_cols+1)).astype(int)
		self.hline = np.zeros((n_rows+1, n_cols)).astype(int)
		self.vertex = np.zeros((n_rows+1, n_cols+1)).astype(int)
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
	def set_lines(self, hline_array, vline_array):
		# Define line placements
		if type(hline_array) is str:
			hline_array = self.lines_str_to_array(hline_array)
		if type(vline_array) is str:
			vline_array = self.lines_str_to_array(vline_array).transpose()
		assert hline_array.shape == self.hline.shape, "hline_array has incorrect shape, should be %r" % self.hline.shape
		assert vline_array.shape == self.vline.shape, "vline_array has incorrect shape, should be %r" % self.vline.shape
		assert (np.min(hline_array)>=-1) & (np.max(hline_array)<=1) & (np.min(vline_array)>=-1) & (np.max(vline_array)<=1), "Some value in hline_array or vline_array is not between -1 and 3."
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
	def edge_coords_around_cell(self, coords):
		y,x = coords
		return [(y,x), (y+1,x), (y,x), (y,x+1)]
	def edges_around_cell(self, coords):
		y,x = coords
		top = self.hline[y,x]
		bottom = self.hline[y+1,x]
		left = self.vline[y,x]
		right = self.vline[y,x+1]
		trbl = np.array([top, right, bottom, left])
		return trbl
	def lines_into_vertex(self, coords):
		y,x = coords
		north, south, east, west = 0, 0, 0, 0
		# return self.vertex[:,y,x]
		# If the vertex is in the middle, it will have all lines from all 4 directions.
		if 0<y:
			north = self.vline[y-1,x]
		else:
			north = -1
		if y<self.n_rows:
			south = self.vline[y,x]
		else:
			south = -1
		if 0<x:
			east = self.hline[y,x-1]
		else:
			east = -1
		if x<self.n_cols:
			west = self.hline[y,x]
		else:
			west = -1
		nesw = np.array([north, east, south, west])
		return nesw
	def update_vertices_from_lines(self):
		# If a line exists, we know vertices at both ends are visited.
		self.vertex[:,:-1][self.hline==1] = 1
		self.vertex[:,1: ][self.hline==1] = 1
		self.vertex[:-1,:][self.vline==1] = 1
		self.vertex[1: ,:][self.vline==1] = 1
		# We can deduce that a vertex is unvisited if all lines into it are impossible.
		unknowns = np.where(self.vertex==0)
		for row,col in zip(*unknowns):
			if np.all(self.lines_into_vertex((row,col))==-1):
				self.vertex[row,col] = -1
	def update_lines_from_numbers(self):
		numbered_squares = np.where(self.number>=0)
		for row,col in zip(*numbered_squares):
			number = self.number[row,col]
			trbl = self.edges_around_cell((row,col))
			n_lines = np.sum(trbl==1)
			n_xs = np.sum(trbl==-1)
			if n_lines + n_xs == 4:
				assert number == n_lines
			elif n_lines == number:
				print("Where TRBL is 0 should now be -1")
			# elif n_lines < number:
			# 	if
		# If vertex is visited, two linse must be true, two false.
		
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






from PIL import Image, ImageDraw, ImageFont
import numpy as np
import re
import os
import itertools

class Grid:
	def __init__(self, dims=[4,4], name="grid"):
		# Set up all variables
		n_rows, n_cols = dims
		self.n_rows = n_rows
		self.n_cols = n_cols
		# vertex[n,i,j] describes the vertex [i,j]. Nth value describes nth edge projecting from vertex, in order NESW.
		self.vertex = np.zeros((4, n_rows+1, n_cols+1)).astype(int)
		self.set_bounding_constraints()
		# cell[x,i,j] describes the cell [i,j]. 
		# 	cell[0] gives the number (0, 1, 2 or 3, or -1 for unknown)
		#	cell[1] gives the number of edges currently drawn around the cell
		#	cell[2] gives the number of edges currently nixed around the cell
		# 	cell[3] gives the shading (1 for in, -1 for outside the bounded area)
		self.cell = np.zeros((4, n_rows, n_cols)).astype(int)
		self.cell[0] += -1
		self.image_filename = name+".png"
	def set_bounding_constraints(self):
		# Set fundamental vertex impossibilities: No edge can go NORTH from top row, to EAST from right row, etc.
		self.vertex[0,0,:] = -1
		self.vertex[1,:,-1] = -1
		self.vertex[2,-1,:] = -1
		self.vertex[3,:,0] = -1
	#
	#	Functions to select views of the grid:
	#
	def hlines(self):
		return self.vertex[3,:,1:]
	def vlines(self):
		return self.vertex[0,1:,:]
	def numbers(self):
		return self.cell[0]
	def shades(self):
		return self.cell[3]
	# def drawn_edges(self):
	# 	return self.drawn_edges[2]
	# 
	#	Functions to define grids: 
	#
	def set_grid(self, number_array):
		# Define an input grid
		if type(number_array) is str:
			number_array = self.numbers_str_to_array(number_array)
		assert number_array.shape == self.cell[0].shape, "Shape of grid and input to set_grid do not match."
		assert np.min(number_array)>=-1, "Values less than -1 detected."
		assert np.max(number_array)<=3, "Values greater than 3 detected."
		self.cell[0] = number_array
		# n_snakes = np.sum(number_array==1) + 2*np.sum(number_array==2) + np.sum(number_array==3)
		# self.snake = np.zeros((n_snakes, 1, 1))
	def numbers_str_to_array(self, number_string):
		rows = number_string.split(" ")
		assert self.n_cols == len(rows[0])
		assert self.n_rows == len(rows)
		number_array = np.zeros_like(self.cell[0])-1
		for i,row in enumerate(rows):
			for j,char in enumerate(row):
				if char in ["0","1","2","3"]:
					number_array[i,j] = int(char)
		return number_array
	def set_lines(self, hline_array, vline_array):
		# Define line placements
		if type(hline_array) is str:
			hline_array = self.lines_str_to_array(hline_array)
		if type(vline_array) is str:
			vline_array = self.lines_str_to_array(vline_array).transpose()
		expected_hline_shape = (self.n_rows+1,self.n_cols)
		expected_vline_shape = (self.n_rows,self.n_cols+1)
		assert hline_array.shape == expected_hline_shape, "hline_array has incorrect shape, should be %r" % expected_hline_shape
		assert vline_array.shape == expected_vline_shape, "vline_array has incorrect shape, should be %r" % expected_vline_shape
		assert (np.min(hline_array)>=-1) & (np.max(hline_array)<=1) & (np.min(vline_array)>=-1) & (np.max(vline_array)<=1), "Some value in hline_array or vline_array is not between -1 and 3."
		# Now, we must apply each known edge from input arrays to vertex grid.
		# First, for every vline, we should indicate that it connects the southern node of a higher-up vertex to the northern node of a lower-down vertex.
		for val in [1, -1]:
			self.vertex[1][:,:-1][hline_array==val] = val
			self.vertex[3][:,1: ][hline_array==val] = val
			self.vertex[0][1: ,:][vline_array==val] = val
			self.vertex[2][:-1,:][vline_array==val] = val
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
	#
	# 	Function to print grids:
	#
	def print_grid(self, include_lines=True, include_numbers=True, include_xs=True, include_ticks=True, print_scale=30):
		# Print grid, with or without lines or numbers
		k = print_scale
		font_path = "/Library/Fonts/Courier New.ttf"
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
			font = ImageFont.truetype(font_path,size=int(k/2))
			for i,j in zip(*np.where(self.numbers()>-1)):
				x = self.numbers()[i,j].astype(str)
				# tex_x = j*k+k/2-font.getsize(x)[0]/2
				# tex_y = i*k+k/2-font.getsize(x)[1]/2
				tex_x = (j+1.5)*k - font.getsize(x)[0]/2.0 # + 1
				tex_y = (i+1.5)*k - font.getsize(x)[1]/2.0 # + 1
				d.text((tex_x, tex_y), x, font=font, fill="#000")
				# print(x, tex_x, tex_y)
		# Draw lines
		if include_lines:
			for i,j in zip(*np.where(self.hlines()==1)):
				x = (j+1)*k
				y = (i+1)*k
				d.line( [(x,y), (x+k,y)], fill="#000")
			for i,j in zip(*np.where(self.vlines()==1)):
				x = (j+1)*k
				y = (i+1)*k
				d.line( [(x,y), (x,y+k)], fill="#000")
		# Draw invalid lines
		if include_xs:
			tw = k/10  # tick (half)-width
			for i,j in zip(*np.where(self.hlines()==-1)):
				x = (j+1)*k + k/2
				y = (i+1)*k
				d.line([x-tw,y-tw,x+tw,y+tw],fill="#aaa")
				d.line([x-tw,y+tw,x+tw,y-tw],fill="#aaa")
			for i,j in zip(*np.where(self.vlines()==-1)):
				x = (j+1)*k
				y = (i+1)*k + k/2
				d.line([x-tw,y-tw,x+tw,y+tw],fill="#aaa")
				d.line([x-tw,y+tw,x+tw,y-tw],fill="#aaa")
		del d
		im.save(self.image_filename)
	#
	#	Update functions
	#
	def get_number_of_edges(self, val=1):
		drawn_left = (self.vlines()[:,:-1]==val)*1
		drawn_right = (self.vlines()[:,1:]==val)*1
		drawn_above = (self.hlines()[:-1,:]==val)*1
		drawn_below = (self.hlines()[1:,:]==val)*1
		return drawn_above + drawn_right + drawn_below + drawn_left
	def refresh_cells(self):
		n_drawn_edges = self.get_number_of_edges(1)
		n_xed_edges = self.get_number_of_edges(-1)
		self.cell[1] = n_drawn_edges
		self.cell[2] = n_xed_edges
	def vertex_coords_around_cell(self,cell_coords):
		#      [1,i,j]  [3,i,j+1]
		#           ij__ij+1
		#    [2,i,j] |i,|  [2,i,j+1]
		#  [0,i+1,j] | j|  [0,i+1,j+1]
		#         i+1j——i+1j+1
		#    [1,i+1,j]  [3,i+1,j+1]
		# Coordinates into self.vertex are returned in order from top left and running clockwise
		i,j = cell_coords
		return [[1,i,j],[3,i,j+1],[2,i,j+1],[0,i+1,j+1],[3,i+1,j+1],[1,i+1,j],[0,i+1,j],[2,i,j]]
	def update_from_numbers(self):
		self.refresh_cells()
		n_needed_edges = self.cell[0]
		n_written_edges = self.cell[1]
		n_nixed_edges = self.cell[2]
		n_open_edges = 4 - n_written_edges - n_nixed_edges
		# In the completed grid, we should have:
		# n_needed_edges == n_written_edges
		# n_written_edges + n_nixed_edges == 4
		numbered_cells = self.cell[0]>=0
		# Action 1: Among numbered cells with unconstrained lines, find those with the maximum number of written lines and nix the rest..
		action_1_cells = numbered_cells & (n_open_edges>0) & (n_needed_edges == n_written_edges)
		self.write_val_around_cell(action_1_cells, -1)
		# for i,j in zip(*np.where(action_1_cells)):
		# 	# Nix remaining lines around this cell
		# 	vertex_edge_coords = self.vertex_coords_around_cell([i,j])
		# 	for n,x,y in vertex_edge_coords:
		# 		if self.vertex[n,x,y]==0:
		# 			self.vertex[n,x,y]=-1
		# Action 2: Among numbered cells, find those where remaining number of unconstrained lines equals the remaining number of lines to draw.
		action_2_cells = numbered_cells & (n_open_edges>0) & (n_open_edges == (n_needed_edges-n_written_edges))
		self.write_val_around_cell(action_2_cells, 1)
		# for i,j in zip(*np.where(action_2_cells)):
		# 	# Nix remaining lines around this cell
		# 	vertex_edge_coords = self.vertex_coords_around_cell([i,j])
		# 	for n,x,y in vertex_edge_coords:
		# 		if self.vertex[n,x,y]==0:
		# 			self.vertex[n,x,y]=1
	def write_val_around_cell(self, cell_bool_array, val):
		for i,j in zip(*np.where(cell_bool_array)):
			vertex_edge_coords = self.vertex_coords_around_cell([i,j])
			for n,x,y in vertex_edge_coords:
				if self.vertex[n,x,y]==0:
					self.vertex[n,x,y]=val
	def write_val_around_vertex(self, vert_bool_array, val):
		for i,j in zip(*np.where(vert_bool_array)):
			open_values = self.vertex[:,i,j] == 0
			self.vertex[open_values,i,j] = val
	def propagate_any_edges(self):
		# We might have a situation where the edge from (0,0) has been drawn east to (0,1), but not drawn from (1,0) west to (0,0).
		# This function ensures all edges (and nixed edges) are reciprocal.
		to_right = self.vertex[1,:,:-1]
		to_left = self.vertex[3,:,1:]
		to_above = self.vertex[0,1:,:]
		to_below = self.vertex[2,:-1,:]
		for val in [1,-1]:
			missing_right = (to_right==0) & (to_left==val)
			missing_left = (to_left==0) & (to_right==val)
			missing_below = (to_below==0) & (to_above==val)
			missing_above = (to_above==0) & (to_below==val)
			self.vertex[1,:,:-1][missing_right] = val
			self.vertex[3,:,1:][missing_left] = val
			self.vertex[0,1:,:][missing_above] = val
			self.vertex[2,:-1,:][missing_below] = val
	def resolve_vertices(self):
		# If 3 of 4 lines into a vertex are nixed, nix the remaining one.
		n_xs_into_verts = np.sum(1*(self.vertex==-1),axis=0)
		nix_remaining_edges = (n_xs_into_verts==3)
		self.write_val_around_vertex(nix_remaining_edges, -1)
		# If 1 line is going into a vertex and there's only 1 way out, write it.
		n_lines_into_verts = np.sum(1*(self.vertex==1),axis=0)
		write_remaining_edge = (n_lines_into_verts==1) & (n_xs_into_verts==2)
		self.write_val_around_vertex(write_remaining_edge, 1)
		# If 2 lines go into a vertex, remaining lines must be nixed.
		n_lines_into_verts = np.sum(1*(self.vertex==1),axis=0)
		nix_remaining_edges = (n_lines_into_verts==2) & (n_xs_into_verts<2)
		self.write_val_around_vertex(nix_remaining_edges, -1)
		
	# def fill_cells(self):
	# 	# For every cell: can we immediately deduce where to draw lines around it?
	# def extend_lines(self):
	# 	# For each line: can we extend it in obvious way?
	# def update_vertices_from_lines(self):
	# 	# For every line in hlines and vlines, render knowledge in vertex array.
	# 	# For every line that exists:
	# 	# 	Vertex-1 must reflect it out
	# 	# 	Vertex-2 must reflect it in
	# 	# For every line that cannot exist:
	# 	# 	Do the same
	# 	#
	# 	# Do hlines first, then vlines:
	# 	for row_i in range(self.hline.shape[0]):
	# 		h_ones = np.where(self.hline[row_i,:]==1)[0]
	# 		h_minus_ones = np.where(self.hline[row_i,:]==-1)[0]
	# 		for col_j in h_ones:
	# 			self.vertex[1,row_i,col_j]=1
	# 			self.vertex[3,row_i,col_j+1]=1
	# 		for col_j in h_minus_ones:
	# 			self.vertex[1,row_i,col_j]=-1
	# 			self.vertex[3,row_i,col_j+1]=-1
	# 	for col_i in range(self.vline.shape[1]):
	# 		v_ones = np.where(self.vline[:,col_i]==1)[0]
	# 		v_minus_ones = np.where(self.vline[:,col_i]==-1)[0]
	# 		for row_j in v_ones:
	# 			self.vertex[2,row_j,col_i]=1
	# 			self.vertex[0,row_j+1,col_i]=1
	# 		for row_j in v_minus_ones:
	# 			self.vertex[2,row_j,col_i]=-1
	# 			self.vertex[0,row_j+1,col_i]=-1
	# def apply_basic_vertex_constraints(self):
	# 	for val in [-1, 1]:
	# 		known_vlines_to_below = self.vertex[0,:-1,:] == val
	# 		known_vlines_from_top = self.vertex[2, 1:,:] == val
	# 		assert np.all(self.vertex[2, 1:,:][known_vlines_to_below] == val)
	# 		assert np.all(self.vertex[0,:-1,:][known_vlines_from_top] == val)
	# 		self.vertex[2,1:, :][known_vlines_to_below] = val
	# 		self.vertex[0,:-1,:][known_vlines_from_top] = val
	# 		known_hlines_to_right = self.vertex[1,:,:-1] == val
	# 		known_hlines_to_left  = self.vertex[3,:, 1:] == val
	# 		assert np.all(self.vertex[2,1:,:][known_vlines_to_below] == val)
	# 		known_vlines_from_top = self.vertex[2][1:,:] == val
	# 		assert np.all(self.vertex[0,:-1,:][known_vlines_from_top] == val)
	# 		self.vertex[2,1:, :][known_vlines_to_below] = val
	# 		self.vertex[0,:-1,:][known_vlines_from_top] = val
	#
	# 	# known_vlines_to_below = self.vertex[0][:-1,:]==1
	# 	# assert np.all(1==self.vertex[2,1:,:][known_vlines_to_below])
	# 	# known_vlines_from_top = self.vertex[2][1:,:]==1
	# 	# assert np.all(1==self.vertex[0,:-1,:][known_vlines_from_top])
	# 	# self.vertex[2,1:, :][known_vlines_to_below] = 1
	# 	# self.vertex[0,:-1,:][known_vlines_from_top] = 1
	# def update_lines_from_vertices(self):
	# 	# For every vertex, look for drawn lines or Xs, and render knowledge in line lists.
	# 	known_vlines = self.vertex[0][:-1,:]==1
	# 	known_vlines = self.vertex[2][1:,:]==1
	# 	for vert_row_i in self.n_rows+1:
	# 		for vert_col_i in self.n_cols+1:
	#
	# 	# For each line,
	# def update_vertices_from_lines(self):
	# 	# If a line exists, we know vertices at both ends are visited.
	# 	self.vertex[:,:-1][self.hline==1] = 1
	# 	self.vertex[:,1: ][self.hline==1] = 1
	# 	self.vertex[:-1,:][self.vline==1] = 1
	# 	self.vertex[1: ,:][self.vline==1] = 1
	# 	# We can deduce that a vertex is unvisited if all lines into it are impossible.
	# 	unknowns = np.where(self.vertex==0)
	# 	for row,col in zip(*unknowns):
	# 		if np.all(self.lines_into_vertex((row,col))==-1):
	# 			self.vertex[row,col] = -1
	# def update_lines_from_numbers(self):
	# 	numbered_squares = np.where(self.numbers()>=0)
	# 	for row,col in zip(*numbered_squares):
	# 		number = self.numbers()[row,col]
	# 		trbl = self.edges_around_cell((row,col))
	# 		n_lines = np.sum(trbl==1)
	# 		n_xs = np.sum(trbl==-1)
	# 		if n_lines + n_xs == 4:
	# 			assert number == n_lines
	# 		elif n_lines == number:
	# 			print("Where TRBL is 0 should now be -1")
			# elif n_lines < number:
			# 	if
		# If vertex is visited, two linse must be true, two false.
	# def update_lines(self):
	# 	# Update line info based on other stuff (cells, vertices, shading)
	# 	for y,x in zip(*np.where(self.numbers()>-1)):
	# 		trbl = self.lines_around_cell([y,x])
	# 		space_used = np.sum(trbl==1)
	# 		space_left = np.sum(trbl==0)
	# 		if (space_used == number):
	# 			# assign remaining spaces to be -1
	# 			# i.e., set any 0 to -1
	#

g = Grid(dims=[6,6], name="wikipedia")
g.set_grid("....0. 33..1. ..12.. ..20.. .1..11 .2....")
# g.set_lines("---... .-...- -..-.. ....-. ..-... ---.-. ----.-",
			# "--...- .-.... .---.. --..-. ..-..- .--..- .-----")
g.set_lines("______ ______ __.-.. __..-. ..-... ---.-. ----.-",
			"______ ______ __--.. __..-. ..-..- .--..- .-----")
g.print_grid()

g.update_from_numbers()
g.resolve_vertices()
g.propagate_any_edges()
g.print_grid()


graph_dict = {0:[1,4], 1:[0,2,5], 2:[1,3,6] ...}
def rectilinear_graph_dict(height,width):
	ar = np.reshape(np.arange(height*width),(height,width))
	output_dict = {x:[] for x in np.arange(height*width)}
	left = ar[:,:-1]
	right = ar[:,1:]
	up = ar[:-1,:]
	down = ar[1:,:]
	for i in range(left.shape[0]):
		for j in range(left.shape[1]):
			output_dict[left[i,j]] += [right[i,j]]
			output_dict[right[i,j]] += [left[i,j]]
	for i in range(up.shape[0]):
		for j in range(up.shape[1]):
			output_dict[up[i,j]] += [down[i,j]]
			output_dict[down[i,j]] += [up[i,j]]
	return output_dict

# number = self.numbers()[y,x]
#
# 		for y,x in zip(*np.where(self.numbers()>-1)):
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

# Incomplete Wikipedia grid
g = Grid(dims=[6,6], name="wikipedia")
g.set_grid("....0. 33..1. ..12.. ..20.. .1..11 .2....")
g.set_lines("---... .-...- -..-.. ....-. ..-... ---.-. ----.-",
			"--...- .-.... .---.. --..-. ..-..- .--..- .-----")
g.update_vertices_from_lines()
g.print_grid()



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





