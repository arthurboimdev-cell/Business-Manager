import tkinter as tk
from tkinter import messagebox
from gui.forms.product_form import ProductForm
from client.api_client import APIClient

class CreateProductDialog(tk.Toplevel):
    def __init__(self, parent, on_success_callback=None):
        super().__init__(parent)
        self.title("Create New Product")
        self.geometry("900x700")
        self.callback = on_success_callback
        
        # Main Container
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Embed Form
        self.form = ProductForm(self.container)
        self.form.pack(fill="both", expand=True)
        
        # Action Buttons
        btn_frame = tk.Frame(self.container)
        btn_frame.pack(fill="x", pady=10)
        
        tk.Button(btn_frame, text="Save Product", command=self.save, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=10).pack(side="right", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy, padx=10).pack(side="right", padx=5)

    def save(self):
        try:
            data = self.form.get_data()
            
            # 1. Create Product
            response = APIClient.add_product(data)
            p_id = response.get('id')
            
            if not p_id:
                raise Exception("Server returned no ID for new product")
            
            # 2. Upload Pending Gallery Images
            pending_imgs = self.form.pending_gallery_images
            if pending_imgs:
                for img in pending_imgs:
                    if 'raw_bytes' in img:
                        try:
                            APIClient.add_product_image(p_id, img['raw_bytes'])
                        except Exception as e:
                            print(f"Failed to upload gallery image {img['id']}: {e}")
            
            messagebox.showinfo("Success", "Product created successfully!")
            
            if self.callback:
                self.callback()
                
            self.destroy()
            
        except ValueError as ve:
            messagebox.showwarning("Validation Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product: {e}")
