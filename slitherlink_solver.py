from PIL import Image, ImageDraw, ImageFont

class Grid:
	def __init__(self, dims=[5,5]):
		self.height = dims[0]
		self.width = dims[1]
		self.grid = "."*self.height*self.width
		self.image_filename = "tmp.png"
		self.draw_grid_scale = 30
	def set_grid(self, numbers="......3.3..3.3..3.3....20"):
		if len(numbers) == self.height*self.width:
			self.grid = numbers
		else:
			print "Error: did not enter valid grid size."
	def show_grid(self):
		k = self.draw_grid_scale
		im = Image.new('RGBA',((self.height+1)*k,(self.width+1)*k), (255,255,255,0))
		d = ImageDraw.Draw(im)
		# Draw tick marks of grid
		for i in range(1,self.height+1):
			for j in range(1,self.width+1):
				d.line([i*k-2,j*k,i*k+2,j*k],fill="#000")
				d.line([i*k,j*k-2,i*k,j*k+2],fill="#000")
		# Draw numbers
		font = ImageFont.load_default()
		for i,x in enumerate(self.grid):
			if x!=".":
				i_x = i%self.height
				i_y = i/self.height
				d.text((i_x*k+k/2-font.getsize(x)[0]/2, i_y*k+k/2-font.getsize(x)[1]/2), x, font=font, fill="#000")
		del d
		im.save(self.image_filename)

a = Grid()
a.set_grid()
a.show_grid()
