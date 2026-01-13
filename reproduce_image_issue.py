
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import base64
import io

# Mock Data
MOCK_IMG_BYTES = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==") # 1x1 Red Dot
MOCK_B64 = base64.b64encode(MOCK_IMG_BYTES).decode('utf-8')

class MockProductTab(tk.Tk):
    def __init__(self):
        super().__init__()
        self.products = [
            {'id': 1, 'title': 'Prod A', 'image': MOCK_B64},
            {'id': 2, 'title': 'Prod B', 'image': None}
        ]
        self.current_preview_image = None
        
        self.lbl_main_img_preview = tk.Label(self, text="No Image", bg="gray", width=20, height=10)
        self.lbl_main_img_preview.pack()
        
        btn_a = tk.Button(self, text="Select A", command=lambda: self.select_product(1))
        btn_a.pack()
        btn_b = tk.Button(self, text="Select B", command=lambda: self.select_product(2))
        btn_b.pack()
        
    def select_product(self, p_id):
        product = next((p for p in self.products if p['id'] == p_id), None)
        print(f"Selected {product['title']}, image data length: {len(product['image']) if product['image'] else 0}")
        self.display_main_image(product['image'])
        
    def display_main_image(self, image_input):
        print(f"Displaying image... Input type: {type(image_input)}")
        if not image_input:
            self.lbl_main_img_preview.config(image="", text="No Image", width=20, height=10)
            self.current_preview_image = None
            print("Cleared Image")
            return
            
        try:
            img_bytes = None
            if isinstance(image_input, bytes):
                img_bytes = image_input
            elif isinstance(image_input, str):
                if "," in image_input:
                    image_input = image_input.split(",")[1]
                img_bytes = base64.b64decode(image_input)
            
            if img_bytes:
                pil_img = Image.open(io.BytesIO(img_bytes))
                pil_img.thumbnail((150, 150))
                tk_img = ImageTk.PhotoImage(pil_img)
                
                self.lbl_main_img_preview.config(image=tk_img, text="", width=150, height=150)
                self.current_preview_image = tk_img 
                print("Image Set Successfully")
        except Exception as e:
            print(f"Error displaying image: {e}")

if __name__ == "__main__":
    app = MockProductTab()
    app.after(1000, lambda: app.select_product(1)) # Auto select A
    app.after(2000, lambda: app.select_product(2)) # Auto select B
    app.after(3000, lambda: app.select_product(1)) # Back to A
    app.after(4000, lambda: app.destroy())
    app.mainloop()
