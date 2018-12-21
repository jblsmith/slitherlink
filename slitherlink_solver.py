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

class Grid:	
	def __init__(self, dims=[4,4]):
		# Set up all variables
	def set_grid(self, number_array):
		# Define an input grid
	def set_lines(self, hline_array, vline_array):
		# Define line placements
	def print_grid(include_lines=True, include_numbers=True):
		# Print grid, with or without lines or numbers
	def fill_cells(self):
		# For every cell: can we immediately deduce where to draw lines around it?
	def extend_lines(self):
		# For each line: can we extend it in obvious way?
	def update_lines(self):
		# Update line info based on other stuff (cells, vertices, shading)
	def update_vertices(self):
		# Update vertex info
	def update_cells(self):
		# Update cell info
	def update_shading(self):
		# Update shade info
	def merge_snakes(self, snake1, snake2):
		# Merge two snakes









