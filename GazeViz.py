# Tony Assi December 2017
# GazeViz 1.0


# Import libraries
from Tkinter import *
from PIL import Image, ImageDraw, ImageTk, ImageOps
import Tkinter
import os


##### VARIABLES #####

# Image preview width and height
preview_width = 1300
preview_height = 700

# Thumbnail size
src_thumbnail_size = 35
dest_thumbnail_size = 40

# Border Size
border_size = 1

# Gaze data
data = []

# Root window 
root = Tkinter.Tk()  
root.title("GAZE VIZ 1.0")

# GUI preview image
gui_img = Tkinter.Label(root)

# Sliders
zoom_slider = Scale(root, from_=1, to=300, showvalue=1, orient=HORIZONTAL, length=350, label="Thumbnail Zoom")
zoom_slider.set(src_thumbnail_size)
size_slider = Scale(root, from_=1, to=300, orient=HORIZONTAL, length=350, label="Thumbnail Size")
size_slider.set(dest_thumbnail_size)
border_slider = Scale(root, from_=0, to=30, orient=HORIZONTAL,  length=350, label="Border Size")
border_slider.set(border_size)

#####################


##### GET COMMAND LINE ARGS #####
args = sys.argv[1:]
img_path = args[0]
data_path = args[1]
#################################


##### SOURCE IMAGE #####
# Load image
src_img = Image.open(img_path)

# Get source image dimensions
src_img_width, src_img_height = src_img.size

print "Load Image: SUCCESS"
#########################


##### DISPLAY IMAGE #####
# Display image width and height
display_img_width = src_img_width
display_img_height = src_img_height

# Create black display image
display_img = Image.new('RGB',(src_img_width, src_img_height))
#########################



##### FUNCTIONS #####
def load_data():
	# Load data file
	data_file = open(data_path,'r') 

	# Read data file
	data_file = data_file.readlines()

	# Get size
	data_width = float( data_file[0].split(',')[0] )
	data_height = float( data_file[0].split(',')[1][:-1] )

	# Parse data file into list
	for line in data_file[1:-1]:
		# Parse X and Y
		x = float( line[:-1].split(',')[0] )
		y = float( line[:-1].split(',')[1] )
		# Scale X and Y to (0,1)
		x = x / data_width
		y = y / data_height
		data.append([x,y])

	print "Load Data: SUCCESS"


def get_square_thumbnail(x, y, src_thumbnail_size, dest_thumbnail_size):
	# Calculate source image X and Y
	src_x = int(x - (src_thumbnail_size / 2))
	src_y = int(y - (src_thumbnail_size / 2))

	# Get square thumbnail
	thumbnail = src_img.crop((src_x, src_y,  src_x + src_thumbnail_size, src_y + src_thumbnail_size))

	return thumbnail


def render():
	# Get slider values
	src_thumbnail_size = zoom_slider.get()
	dest_thumbnail_size = size_slider.get()
	border_size = border_slider.get()

	# Update label on zoom slider
	zoom = float(dest_thumbnail_size*dest_thumbnail_size) / float(src_thumbnail_size*src_thumbnail_size)
	zoom_slider.configure(label="Source Thumbnail Size      (Zoom "+ str(zoom)+")")

	# Create black display image
	display_img = Image.new('RGB',(src_img_width, src_img_height))

	# For each data point, draw thumbnail
	for xy in data:
		# Scale XY to (0, width) and (0, height)
		x = xy[0] * display_img_width
		y = xy[1] * display_img_height

		# Get square thumbnail
		thumbnail = get_square_thumbnail(x, y, src_thumbnail_size, dest_thumbnail_size)

		# Calculate destination image X and Y
		dest_x = int(x - (dest_thumbnail_size / 2))
		dest_y = int(y - (dest_thumbnail_size / 2))

		# Draw border
		x_border = dest_x - border_size
		y_border = dest_y - border_size
		border_length = dest_thumbnail_size + (border_size * 2)
		border = Image.new('RGB',(border_length, border_length), (255, 255, 255))
		display_img.paste(border, (x_border, y_border,  x_border + border_length, y_border + border_length) )
	
		# Resize source thumbnail to destination thumbnail
		thumbnail = thumbnail.resize((dest_thumbnail_size, dest_thumbnail_size), Image.ANTIALIAS)

		# Draw thumbnail on display image
		display_img.paste(thumbnail, (dest_x, dest_y,  dest_x + dest_thumbnail_size, dest_y + dest_thumbnail_size) )

	return display_img
	print "Render Image: SUCCESS"

def render_preview():
	# Get rendered image
	img = render()

	# Display image width and height
	display_img_width = src_img_width
	display_img_height = src_img_height

	# Make sure image dimensions are smaller than preview size
	# and maintains source aspect ratio
	if(src_img_width > preview_width):
		display_img_height = display_img_height * preview_width / src_img_width
		display_img_width = preview_width
	if(src_img_height > preview_height):
		display_img_width = display_img_width * preview_height / display_img_height
		display_img_height = preview_height

	# Cast image width and height to integers 
	display_img_width = int(display_img_width)
	display_img_height = int(display_img_height)

	# Resize image to preview
	preview_img = img.resize((display_img_width,display_img_height), Image.ANTIALIAS)

	# Update GUI preview image
	tkimage = ImageTk.PhotoImage(preview_img)
	gui_img.configure(image=tkimage)
	gui_img.image = tkimage

	print "Render Preview: SUCCESS"
	return preview_img

def save_image():
	# Get rendered image
	img = render()

	# Save image 
	img.save('OUTPUT'+str(zoom_slider.get())+'-'+str(size_slider.get())+'-'+str(border_slider.get())+'.png', 'PNG')

	print "Save Image: SUCCESS" 

def save_animation():
	# Get slider values
	src_thumbnail_size = zoom_slider.get()
	dest_thumbnail_size = size_slider.get()
	border_size = border_slider.get()

	# Output directory
	output_dir = 'OUTPUT'+str(zoom_slider.get())+'-'+str(size_slider.get())+'-'+str(border_slider.get())
	
	# Make directory to put images sequence in
	if os.path.isdir(output_dir) == False:
		os.makedirs(output_dir)

	# Create black display image
	display_img = Image.new('RGB',(src_img_width, src_img_height))

	# For each data point, draw thumbnail
	for i, xy in enumerate(data):
		# Scale XY to (0, width) and (0, height)
		x = xy[0] * display_img_width
		y = xy[1] * display_img_height

		# Calculate source image X and Y
		src_x = int(x - (src_thumbnail_size / 2))
		src_y = int(y - (src_thumbnail_size / 2))

		# Get thumbnail
		thumbnail = src_img.crop((src_x, src_y,  src_x + src_thumbnail_size, src_y + src_thumbnail_size))

		# Calculate destination image X and Y
		dest_x = int(x - (dest_thumbnail_size / 2))
		dest_y = int(y - (dest_thumbnail_size / 2))

		# Draw border
		x_border = dest_x - border_size
		y_border = dest_y - border_size
		border_length = dest_thumbnail_size + (border_size * 2)
		border = Image.new('RGB',(border_length, border_length), (255, 255, 255))
		display_img.paste(border, (x_border, y_border,  x_border + border_length, y_border + border_length) )
	
		# Resize source thumbnail to destination thumbnail
		thumbnail = thumbnail.resize((dest_thumbnail_size, dest_thumbnail_size), Image.ANTIALIAS)

		# Draw thumbnail on display image
		display_img.paste(thumbnail, (dest_x, dest_y,  dest_x + dest_thumbnail_size, dest_y + dest_thumbnail_size) )

		# Save image
		display_img.save(output_dir+'/'+str(i)+'.png', 'PNG')
		print str(i) + ' / ' + str(len(data)) + '  (' + str(int(float(i)/float(len(data))*100)) + '%)' 
	print "Save Animation: SUCCESS"
########################


# Load data
load_data()

# Get preview image
preview_img = render_preview()


##### GUI #####

# Convert the Image object into a TkPhoto object
#tkimage = ImageTk.PhotoImage(preview_img)
# Put it in the display window
#gui_img = Tkinter.Label(root, image=tkimage)
gui_img.pack(side=LEFT) 

# Zoom slider
zoom_slider.pack()

# Size slider
size_slider.pack()

# Border slider
border_slider.pack()

# Render button
render_button = Button(root, text="RENDER PREVIEW", command=render_preview)
render_button.pack()

# Save button
save_button = Button(root, text="SAVE IMAGE", command=save_image)
save_button.pack()

# Save animation
save_animation_button = Button(root, text="SAVE ANIMATION", command=save_animation)
save_animation_button.pack()

# Start the GUI
root.mainloop() 
################
