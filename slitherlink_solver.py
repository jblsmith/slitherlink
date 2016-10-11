from PIL import Image, ImageDraw, ImageFont
import numpy as np

class Grid:
	def __init__(self, dims=[4,4]):
		self.cellsize = dims
		self.ticksize = (dims[0]+1,dims[1]+1)
		self.grid = "."*np.prod(self.cellsize)
		self.image_filename = "tmp.png"
		self.draw_grid_scale = 30
	def set_grid(self, numbers="3...3.3.3.3...20"):
		if len(numbers) == np.prod(self.cellsize):
			self.grid = numbers
		else:
			print "No action; did not enter valid grid size."
	def set_lines(self, lines):
		print self.width -1 + self.height-1 + 2*(self.width - 1)*(self.height - 1)
		if len(lines) == self.width -1 + self.height -1 + 2*(self.width - 1)*(self.height - 1):
			self.lines = lines
		else:
			print "No action; number of lines incorrect."
	def show_grid(self):
		k = self.draw_grid_scale
		x_off = k
		y_off = k
		im = Image.new('RGB',((self.ticksize[0]+1)*k,(self.ticksize[1]+1)*k), (255,255,255))
		d = ImageDraw.Draw(im)
		# Draw tick marks of grid
		for i in range(1,1+self.ticksize[0]):
			for j in range(1,1+self.ticksize[1]):
				d.line([i*k-2,j*k,i*k+2,j*k],fill="#000")
				d.line([i*k,j*k-2,i*k,j*k+2],fill="#000")
		# Draw numbers
		font = ImageFont.load_default()
		for i,x in enumerate(self.grid):
			if x!=".":
				i_x = i%self.cellsize[0]+1
				i_y = i/self.cellsize[0]+1
				tex_x = i_x*k+k/2-font.getsize(x)[0]/2
				tex_y = i_y*k+k/2-font.getsize(x)[1]/2
				d.text((tex_x, tex_y), x, font=font, fill="#000")
		del d
		# Save output
		im.save(self.image_filename)

a = Grid()
# a.width = 1
# a.height = 1
# a.set_grid(".")
# a.set_lines()
a.set_grid()
a.show_grid()
# a.set_lines("---.-..-.-.-..--..-.-.-..-.---.")

base = Image.open('crying.jpg').convert('RGBA')
