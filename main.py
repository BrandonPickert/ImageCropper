import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageCropperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Space Image Cropper")

        # Modern, space-like styling
        self.root.config(bg="#1E1E1E")  # Dark background
        self.canvas_bg_color = "#2A2A2A"
        self.button_color = "#2D2DFF"
        self.text_color = "#FFFFFF"
        self.highlight_color = "#FF5733"
        self.cross_cursor = "cross"

        # Set up folder paths
        self.input_folder = ""
        self.output_folder = ""
        self.images = []
        self.current_image_index = -1
        self.current_image = None
        self.tk_img = None
        self.crop_start = None
        self.rect_id = None

        # Tkinter UI Elements
        self.canvas = tk.Canvas(root, width=800, height=600, bg=self.canvas_bg_color)
        self.canvas.pack()

        self.counter_label = tk.Label(root, text="Images Left: 0", fg=self.text_color, bg="#1E1E1E", font=("Helvetica", 14))
        self.counter_label.pack(pady=10)

        self.select_input_button = tk.Button(root, text="Select Input Folder", command=self.select_input_folder,
                                             bg=self.button_color, fg=self.text_color, font=("Helvetica", 12))
        self.select_input_button.pack(pady=5)

        self.select_output_button = tk.Button(root, text="Select Output Folder", command=self.select_output_folder,
                                              bg=self.button_color, fg=self.text_color, font=("Helvetica", 12))
        self.select_output_button.pack(pady=5)

        # "Begin" button with green styling
        self.begin_button = tk.Button(root, text="Begin", command=self.next_image,
                                      bg="#28a745", fg=self.text_color, font=("Helvetica", 12), state=tk.DISABLED)
        self.begin_button.pack(pady=10)

        self.canvas.bind("<Button-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.update_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

    def select_input_folder(self):
        """Select the input folder and load images."""
        self.input_folder = filedialog.askdirectory()
        if self.input_folder:
            self.load_images()

    def select_output_folder(self):
        """Select the output folder where cropped images will be saved."""
        self.output_folder = filedialog.askdirectory()
        if self.output_folder and self.input_folder:
            self.load_images()  # Re-check uncropped images when the output folder is selected

    def load_images(self):
        """Scan the input and output folder and find images that haven't been cropped yet."""
        if not self.input_folder or not self.output_folder:
            messagebox.showwarning("Warning", "Please select both input and output folders.")
            return

        # Get the list of files from input and output directories
        input_files = set(f for f in os.listdir(self.input_folder) if f.endswith(".jpg") or f.endswith(".jpeg"))
        output_files = set(os.listdir(self.output_folder))

        # Only keep images that haven't been cropped yet (not present in output folder)
        self.images = list(input_files - output_files)

        # Sort the image list to ensure order
        self.images.sort()

        # Reset index and update counter
        self.current_image_index = -1
        self.update_counter()

        # Enable "Begin" button if there are images to process
        if self.images:
            self.begin_button.config(state=tk.NORMAL)
        else:
            messagebox.showinfo("Info", "No uncropped images found.")

    def update_counter(self):
        """Update the image counter label."""
        self.counter_label.config(text=f"Images Left: {len(self.images) - self.current_image_index - 1}")

    def next_image(self):
        """Load the next image that hasn't been cropped yet."""
        self.load_images()  # Always reload image list to ensure it’s up-to-date
        self.current_image_index += 1
        if self.current_image_index < len(self.images):
            image_path = os.path.join(self.input_folder, self.images[self.current_image_index])
            self.current_image = Image.open(image_path)
            self.display_image()
        else:
            messagebox.showinfo("Info", "No more images to crop.")
            self.current_image_index -= 1
            self.begin_button.config(state=tk.DISABLED)

    def display_image(self):
        """Display the current image on the canvas."""
        if self.current_image:
            img_resized = self.current_image.resize((800, 600), Image.Resampling.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(img_resized)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

    def start_crop(self, event):
        """Start the cropping area by recording the mouse's starting position."""
        if self.current_image:
            self.crop_start = (event.x, event.y)
            self.canvas.config(cursor=self.cross_cursor)
            # Remove any existing rectangle
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_id = None

    def update_crop(self, event):
        """Update the selection rectangle as the user drags the mouse."""
        if self.crop_start:
            x1, y1 = self.crop_start
            x2, y2 = event.x, event.y
            if self.rect_id:
                self.canvas.coords(self.rect_id, x1, y1, x2, y2)
            else:
                self.rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.highlight_color, width=2, dash=(5, 2), fill='gray', stipple='gray25')

    def end_crop(self, event):
        """End the cropping and save the cropped area."""
        if self.current_image and self.crop_start:
            crop_end = (event.x, event.y)
            # Calculate the cropping rectangle on the original image dimensions
            x1, y1 = self.crop_start
            x2, y2 = crop_end

            # Get the actual image size (not the resized 800x600)
            img_width, img_height = self.current_image.size

            # Get the ratios between the displayed canvas size and actual image size
            canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
            ratio_x = img_width / canvas_width
            ratio_y = img_height / canvas_height

            # Translate the canvas coordinates back to the image coordinates
            left = int(min(x1, x2) * ratio_x)
            top = int(min(y1, y2) * ratio_y)
            right = int(max(x1, x2) * ratio_x)
            bottom = int(max(y1, y2) * ratio_y)

            cropped_image = self.current_image.crop((left, top, right, bottom))

            self.save_image(cropped_image)
            self.crop_start = None
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            self.canvas.config(cursor="arrow")

            # Automatically go to the next image after saving
            self.next_image()

    def save_image(self, image):
        """Save the cropped image with the same name in the output folder."""
        if not self.output_folder:
            messagebox.showwarning("Warning", "Please select an output folder first.")
            return

        original_filename = self.images[self.current_image_index]
        output_path = os.path.join(self.output_folder, original_filename)

        image.save(output_path)
        self.update_counter()
        self.load_images()  # Reload image list to avoid cropping the same image as others

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropperApp(root)
    root.mainloop()
