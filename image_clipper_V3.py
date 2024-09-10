# -*- coding: utf-8 -*-
"""
Note 1: Initial Loading may take awhile before it reacts to keys below, depending on number of images to load in selected folder 
Note 2: Edit variables "crop_width" and "crop_height" to the desired fixed output cropped image sizes
Note 3: Edit variable "filetype" to the desired output file type

Keyboard  - Left/Right to go to next image
Middle    - Mouse scroll to zoom in/out
Mouse     - Left click to clip image

"""
import os
import time  # For profiling and debugging delays
from tkinter import Tk, Canvas, filedialog, NW
from PIL import Image, ImageTk
from datetime import datetime

# Define crop area (fixed size)
crop_width = 536  # Set your desired width here
crop_height = 240  # Set your desired height here
# Output image shall be resize to this pixel size and i.e. aspect ratio
filetype = "png" # otherwise can use "jpg" , "bmp"


class ImageCropper:
    def __init__(self, root, image_folder, crop_width, crop_height):
        self.root = root
        self.root.title("Image Cropper")

        # Maximize the window to the screen size
        self.root.state('zoomed')

        self.image_folder = image_folder
        self.images = [f for f in os.listdir(image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
        self.current_image_index = 0

        self.crop_width = crop_width
        self.crop_height = crop_height
        self.zoom_factor = 1.0

        # Image canvas
        self.canvas = Canvas(root, cursor="cross")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Motion>", self.preview_crop_area)  # Bind mouse movement for preview
        self.canvas.bind("<ButtonPress-1>", self.start_crop)  # Bind left-click to confirm crop

        # Bind keyboard events for left/right arrow navigation
        self.root.bind("<Left>", self.load_previous_image)
        self.root.bind("<Right>", self.load_next_image)

        # Bind mouse scroll for zooming
        self.canvas.bind("<MouseWheel>", self.zoom)

        # Load the first image
        self.load_image(self.images[self.current_image_index])

        # Placeholder for preview rectangle
        self.rect = None

    def load_image(self, filename):
        start_time = time.time()  # Start timing

        try:
            self.image_path = os.path.join(self.image_folder, filename)
            self.original_image = Image.open(self.image_path)

            # Resize only for display purposes, but keep the original for cropping
            self.display_image = self.original_image.copy()  # Copy to avoid altering the original image
            self.display_image.thumbnail((int(self.original_image.width * self.zoom_factor),
                                          int(self.original_image.height * self.zoom_factor)), Image.Resampling.LANCZOS)

            self.tk_image = ImageTk.PhotoImage(self.display_image)
            self.canvas.create_image(0, 0, image=self.tk_image, anchor=NW)

            # Ensure the rectangle is on top of the image
            if self.rect:
                self.canvas.tag_raise(self.rect)

        except Exception as e:
            print(f"Error loading image: {e}")

        print(f"Image loaded in {time.time() - start_time:.2f} seconds")  # Print the time taken

    def load_next_image(self, event=None):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.load_image(self.images[self.current_image_index])

    def load_previous_image(self, event=None):
        self.current_image_index = (self.current_image_index - 1) % len(self.images)
        self.load_image(self.images[self.current_image_index])

    def zoom(self, event):
        try:
            if event.delta > 0:
                self.zoom_factor *= 1.1  # Zoom in
            else:
                self.zoom_factor /= 1.1  # Zoom out
            self.load_image(self.images[self.current_image_index])
        except Exception as e:
            print(f"Error applying zoom: {e}")

    def preview_crop_area(self, event):
        try:
            # Update the coordinates of the preview rectangle as the mouse moves
            x1 = event.x
            y1 = event.y
            x2 = x1 + self.crop_width
            y2 = y1 + self.crop_height

            # If a rectangle already exists, update it. Otherwise, create it.
            if self.rect:
                self.canvas.coords(self.rect, x1, y1, x2, y2)
            else:
                self.rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)

            # Ensure the rectangle is always on top of the image
            self.canvas.tag_raise(self.rect)
        except Exception as e:
            print(f"Error updating preview crop area: {e}")

    def start_crop(self, event):
        try:
            # Get coordinates from the canvas
            start_x_canvas = event.x
            start_y_canvas = event.y

            # Calculate the crop area size and adjust for zoom
            crop_width_zoomed = int(self.crop_width / self.zoom_factor)
            crop_height_zoomed = int(self.crop_height / self.zoom_factor)

            # Convert canvas coordinates to original image coordinates
            start_x = int(start_x_canvas / self.zoom_factor)
            start_y = int(start_y_canvas / self.zoom_factor)
            end_x = int(start_x + crop_width_zoomed)
            end_y = int(start_y + crop_height_zoomed)

            # Ensure coordinates are within bounds of the original image
            start_x = max(0, min(start_x, self.original_image.width))
            start_y = max(0, min(start_y, self.original_image.height))
            end_x = max(0, min(end_x, self.original_image.width))
            end_y = max(0, min(end_y, self.original_image.height))

            # Crop and save the image using the original image
            datetime_at_click = datetime.now().strftime('_%Y-%m-%d_%H%M%S')
            cropped_image = self.original_image.crop((start_x, start_y, end_x, end_y))

            # Resize the cropped image to the desired width and height
            cropped_image_resized = cropped_image.resize((self.crop_width, self.crop_height), Image.Resampling.LANCZOS)

            filename = f"cropped_{self.images[self.current_image_index]}"[:-4]+str(datetime_at_click)+"."+filetype
            #cropped_image.save(f"cropped_{self.images[self.current_image_index]}"+str(datetime_at_click), format="PNG")
            cropped_image_resized.save(filename, format="PNG")
            print(f"Cropped image saved as cropped_{self.images[self.current_image_index]}")
        except Exception as e:
            print(f"Error saving image: {e}")

# Setup application window
if __name__ == "__main__":
    root = Tk()

    # Folder selection
    image_folder = filedialog.askdirectory(title="Select Image Folder")
    if not image_folder:
        print("No folder selected. Exiting.")
        root.destroy()

    app = ImageCropper(root, image_folder, crop_width, crop_height)
    root.mainloop()
