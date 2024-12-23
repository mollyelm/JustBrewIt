import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

root = tk.Tk()
root.title("Just Brew It")
root.configure(bg="#F5DEB3")

borderthickness = 10

canvas_width = 1600
canvas_height = 900

# define proportions
cauldron_width_ratio = 0.25  # 28% of canvas width
cauldron_height_ratio = 0.50  # 28% of canvas height
oval_width_ratio = 0.30  # 25% of canvas width
oval_height_ratio = 0.53  # 25% of canvas height

cauldron_width = int(canvas_width * cauldron_width_ratio)
cauldron_height = int(canvas_height * cauldron_height_ratio)

oval_width = int(canvas_width * oval_width_ratio)
oval_height = int(canvas_height * oval_height_ratio)

# create canvas
canvas = tk.Canvas(root, bg="#F5DEB3", highlightthickness=borderthickness, highlightbackground="#361e13", highlightcolor="#8B4513")
canvas.config(width=canvas_width, height=canvas_height)
canvas.grid(row=0, column=0, sticky="nsew")

# avatar oval (to be replaced by hand drawn image)
large_image = Image.new("RGBA", (oval_width, oval_height), color="#F5DEB3")
draw = ImageDraw.Draw(large_image)
draw.ellipse([100, 50, oval_width, oval_height], fill="#f7e9e2", outline="#361e13", width=10)

image = large_image.resize((oval_width, oval_height), Image.Resampling.LANCZOS)

# pil -> tk, useful for getting rid of super jagged pixels. 
oval_image = ImageTk.PhotoImage(image)

# places avatar oval location
canvas.create_image(int(canvas_width * 0.01), int(canvas_height * 0.01), anchor="nw", image=oval_image)

# cauldron (to be replaced by hand drawn image and gif frames)
cauldron_gif = Image.open("cauldron.gif")

# store frames
frames = []
for frame in range(cauldron_gif.n_frames):
    cauldron_gif.seek(frame)
    resized_frame = cauldron_gif.copy().resize((cauldron_width, cauldron_height), Image.Resampling.LANCZOS)
    frame_image = ImageTk.PhotoImage(resized_frame)
    frames.append(frame_image)

# places cauldron location
image_on_canvas = canvas.create_image(int(canvas_width * 0.192), int(canvas_height * 0.76), image=frames[0])

# animate the cauldron
def update_frame(frame):
    canvas.itemconfig(image_on_canvas, image=frames[frame])  # Update the canvas with the new frame
    root.after(100, update_frame, (frame + 1) % len(frames))  # Loop through the frames

# start the cauldron animation
update_frame(0)

# start the gui
root.mainloop()
