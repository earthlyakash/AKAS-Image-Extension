import sys, os, platform, subprocess
from send2trash import send2trash
from tkinter import Tk, Canvas, Frame, Button, Scale, Label, filedialog, HORIZONTAL, NW, messagebox
from tkinter.ttk import Style
from PIL import Image, ImageTk, ImageOps
from psd_tools import PSDImage
from tkinter import Entry, Menu, Toplevel, StringVar, OptionMenu

from PIL import ImageDraw, ImageFont
from akas_decoder import decode_akas
from pdf2image import convert_from_path
from pathlib import Path, PurePath
import sys, os




class MaayraImageViewer:
    def __init__(self, file_path=None):
        self.supported_exts = (
    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp", ".ico", ".ppm", ".pgm", ".tga", ".dds", ".psd", ".psb", ".akas",".pdf")

        self.root = Tk()
        self.root.title("🖼️ AKAS Image Viewer")
        self.root.geometry("1100x800")
        self.root.configure(bg="#121212")

        style = Style()
        style.configure("TButton", padding=6, relief="flat", background="#121212", foreground="#454545")

        self.crop_mode = False
        self.draw_mode = False
        self.dark_mode = True
        self.fullscreen = False
        self.crop_start = None
        self.drawn_lines = []
        self.akas_frames = []
        self.editing_enabled = False
        self.after_id = None
        self.pdf_pages = []
        self.pdf_path = None
        self.pdf_page_index = 0
        self.active_ext_filter = None
        self.full_image_list = []  # Holds unfiltered list




        self.topbar = Frame(self.root, bg="#121212")
        self.topbar.pack(side="top", fill="x")
        

        self.filename_label = Label(self.topbar, text="", bg="#121212", fg="#454545", font=("Segoe UI", 12))
        self.filename_label.pack(side="top", pady=5)
        self.file_filter_var = StringVar(value="Show All")
        filter_options = ["Show All"] + [ext.upper() for ext in self.supported_exts]
        self.file_filter_menu = OptionMenu(self.topbar, self.file_filter_var, *filter_options, command=self.apply_file_filter)
        self.file_filter_menu.config(bg="#262626", fg="#eeeeee", font=("Segoe UI", 10), bd=0, relief="flat")
        self.file_filter_menu.pack(side="right", padx=10)

        Button(self.topbar, text="✏️ Edit Image", bg="#262626", fg="#eeeeee", relief="flat", font=("Segoe UI", 10), bd=0, command=self.enable_edit_tools).pack(side="left", padx=5)
        Button(self.topbar, text="💾 Save Image", bg="#262626", fg="#eeeeee", relief="flat", font=("Segoe UI", 10), bd=0, command=self.save_edited_image).pack(side="left", padx=5)
        Button(self.topbar, text="🔃 Rotate ↻", bg="#121212", fg="#454545", relief="flat", font=("Segoe UI", 10), bd=0, command=self.rotate_clockwise).pack(side="left", padx=5)
        Button(self.topbar, text="🔁 Rotate ↺", bg="#121212", fg="#454545", relief="flat", font=("Segoe UI", 10), bd=0, command=self.rotate_counterclockwise).pack(side="left", padx=5)
        Button(self.topbar, text="↔️ Flip H", bg="#121212", fg="#454545", relief="flat", font=("Segoe UI", 10), bd=0, command=self.flip_horizontal).pack(side="left", padx=5)
        Button(self.topbar, text="↕️ Flip V", bg="#121212", fg="#454545", relief="flat", font=("Segoe UI", 10), bd=0, command=self.flip_vertical).pack(side="left", padx=5)
        Button(self.topbar, text="🗑️ Delete", bg="#121212", fg="#454545", relief="flat", font=("Segoe UI", 10), bd=0, command=self.delete_image).pack(side="left", padx=5)
        Button(self.topbar, text="🖨️ Print", bg="#121212", fg="#454545", relief="flat", font=("Segoe UI", 10), bd=0, command=self.print_image).pack(side="left", padx=5)
        Button(self.topbar, text="📤 Share", bg="#121212", fg="#454545", relief="flat", font=("Segoe UI", 10), bd=0, command=self.share_image).pack(side="left", padx=5)
        Button(self.topbar, text="🌀 AKAS Converter", command=self.open_akas_converter, bg="#121212", fg="#e0e0e0", relief="flat", font=("Segoe UI", 10)).pack(side="left", padx=5)


        self.tool_frame = Frame(self.topbar, bg="#121212")
        self.tool_frame.pack(side="right", padx=5)
        self.tool_buttons = []
        self.create_tool_buttons()
        self.set_tool_buttons_visibility(False)

        self.canvas = Canvas(self.root, bg="#121212", highlightthickness=0, cursor="fleur")
        self.canvas.pack(fill="both", expand=True)

        self.bottombar = Frame(self.root, bg="#121212")
        self.bottombar.pack(side="bottom", fill="x", pady=10)

        self.zoom_slider = Scale(self.bottombar, from_=10, to=200, orient=HORIZONTAL, showvalue=0, command=self.slider_zoom,
                                 length=200, bg="#121212", troughcolor="#333", fg="#454545", highlightthickness=0)
        self.zoom_slider.set(100)
        self.zoom_slider.pack(side="left", padx=20)

        self.zoom_label = Label(self.bottombar, text="100%", bg="#121212", fg="#454545")
        self.zoom_label.pack(side="left")

        self.navbar = Frame(self.bottombar, bg="#121212")
        self.navbar.pack()

        Button(self.navbar, text="⬅️ Prev", bg="#121212", fg="#454545", relief="flat", command=self.prev_image, font=("Segoe UI", 10), bd=0).pack(side="left", padx=10)
        Button(self.navbar, text="📂 Open", bg="#121212", fg="#454545", relief="flat", command=self.open_image, font=("Segoe UI", 10), bd=0).pack(side="left", padx=10)
        Button(self.navbar, text="📁 Open Bulk", bg="#121212", fg="#454545", relief="flat", command=self.open_bulk_folder, font=("Segoe UI", 10), bd=0).pack(side="left", padx=10)
        Button(self.navbar, text="➡️ Next", bg="#121212", fg="#454545", relief="flat", command=self.next_image, font=("Segoe UI", 10), bd=0).pack(side="left", padx=10)

        self.image_info = Label(self.bottombar, text="", bg="#121212", fg="#454545")
        self.image_info.pack(side="right", padx=20)

        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<MouseWheel>", self.mouse_zoom)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Up>", lambda e: self.adjust_zoom(1.1))
        self.root.bind("<Down>", lambda e: self.adjust_zoom(0.9))
        self.root.bind("<Delete>", self.delete_image)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.show_context_menu)




        self.image_paths = []
        self.current_index = 0
        self.original_image = None
        self.tk_image = None
        self.fit_scale = 1.0
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.last_pan = None

        if file_path and os.path.exists(file_path):
            self.load_image_from_path(file_path)

        self.root.mainloop()

    def enable_edit_tools(self):
        self.editing_enabled = True
        self.set_tool_buttons_visibility(True)

    def create_tool_buttons(self):
        self.tool_buttons = [
            Button(self.tool_frame, text="✂️ Crop", command=self.activate_crop),
            Button(self.tool_frame, text="📐 Resize", command=self.resize_image_popup),
            Button(self.tool_frame, text="🎨 Filters", command=self.show_filter_menu),
            Button(self.tool_frame, text="✏️ Draw", command=self.toggle_draw_mode),
            Button(self.tool_frame, text="🔡 Text", command=self.add_text_popup),
            Button(self.tool_frame, text="🌓 Mode", command=self.toggle_dark_light),
            Button(self.tool_frame, text="🧩 Fullscreen", command=self.toggle_fullscreen),
        ]
        for btn in self.tool_buttons:
            btn.configure(bg="#262626", fg="#eeeeee", relief="flat", font=("Segoe UI", 10), bd=0)

    def set_tool_buttons_visibility(self, visible):
        for btn in self.tool_buttons:
            btn.pack_forget() if not visible else btn.pack(side="left", padx=2)

    def save_edited_image(self):
        if not self.original_image or not self.image_paths:
            return
        original_path = self.image_paths[self.current_index]
        base, ext = os.path.splitext(original_path)
        edited_path = f"{base}_edited{ext}"
        self.original_image.save(edited_path)
        messagebox.showinfo("Saved", f"Image saved as: {os.path.basename(edited_path)}")

    def show_context_menu(self, event):
        if not self.image_paths:
            return

        menu = Menu(self.root, tearoff=0)

        # 🖼️ Image submenu
        image_menu = Menu(menu, tearoff=0)
        image_menu.add_command(label="✏️ Edit Image", command=self.enable_edit_tools)
        image_menu.add_command(label="💾 Save Image", command=self.save_edited_image)
        image_menu.add_command(label="🗑️ Delete", command=self.delete_image)
        image_menu.add_command(label="🖨️ Print", command=self.print_image)
        image_menu.add_command(label="📤 Share", command=self.share_image)

        # 🔄 Transform submenu
        transform_menu = Menu(menu, tearoff=0)
        transform_menu.add_command(label="🔃 Rotate ↻", command=self.rotate_clockwise)
        transform_menu.add_command(label="🔁 Rotate ↺", command=self.rotate_counterclockwise)
        transform_menu.add_command(label="↔️ Flip Horizontal", command=self.flip_horizontal)
        transform_menu.add_command(label="↕️ Flip Vertical", command=self.flip_vertical)

        # 🧰 Tools submenu
        tools_menu = Menu(menu, tearoff=0)
        tools_menu.add_command(label="✂️ Crop", command=self.activate_crop)
        tools_menu.add_command(label="📐 Resize", command=self.resize_image_popup)
        tools_menu.add_command(label="🎨 Filters", command=self.show_filter_menu)
        tools_menu.add_command(label="🔡 Add Text", command=self.add_text_popup)

        # ⚙️ View submenu
        view_menu = Menu(menu, tearoff=0)
        view_menu.add_command(label="🌓 Toggle Mode", command=self.toggle_dark_light)
        view_menu.add_command(label="🧩 Toggle Fullscreen", command=self.toggle_fullscreen)
        

        # 📁 File submenu
        file_menu = Menu(menu, tearoff=0)
        file_menu.add_command(label="📁 Open File Location", command=self.open_file_location)
        file_menu.add_command(label="🧾 Properties", command=self.open_properties)

        # Add submenus to root menu
        menu.add_cascade(label="🖼️ Image", menu=image_menu)
        menu.add_cascade(label="🔄 Transform", menu=transform_menu)
        menu.add_cascade(label="🧰 Tools", menu=tools_menu)
        menu.add_cascade(label="⚙️ View", menu=view_menu)
        menu.add_cascade(label="📁 File", menu=file_menu)

        # Show the menu
        menu.tk_popup(event.x_root, event.y_root)

    def open_file_location(self):
        if self.image_paths:
            path = os.path.abspath(self.image_paths[self.current_index])
            folder = os.path.dirname(path)
            if platform.system() == "Windows":
                subprocess.run(f'explorer /select,"{path}"')
            elif platform.system() == "Darwin":
                subprocess.run(["open", "--reveal", path])
            else:
                subprocess.run(["xdg-open", folder])
    
    def open_properties(self):
        if platform.system() != "Windows":
            messagebox.showinfo("Unsupported", "This feature is only available on Windows.")
            return

        try:
            import ctypes
            from ctypes import wintypes

            path = os.path.abspath(self.image_paths[self.current_index])

            ShellExecuteEx = ctypes.windll.shell32.ShellExecuteExW
            SEE_MASK_INVOKEIDLIST = 0x0000000C

            class SHELLEXECUTEINFO(ctypes.Structure):
                _fields_ = [("cbSize", wintypes.DWORD),
                            ("fMask", wintypes.ULONG),
                            ("hwnd", wintypes.HWND),
                            ("lpVerb", wintypes.LPCWSTR),
                            ("lpFile", wintypes.LPCWSTR),
                            ("lpParameters", wintypes.LPCWSTR),
                            ("lpDirectory", wintypes.LPCWSTR),
                            ("nShow", ctypes.c_int),
                            ("hInstApp", wintypes.HINSTANCE),
                            ("lpIDList", ctypes.c_void_p),
                            ("lpClass", wintypes.LPCWSTR),
                            ("hkeyClass", wintypes.HKEY),
                            ("dwHotKey", wintypes.DWORD),
                            ("hIcon", wintypes.HANDLE),
                            ("hProcess", wintypes.HANDLE)]

            sei = SHELLEXECUTEINFO()
            sei.cbSize = ctypes.sizeof(SHELLEXECUTEINFO)
            sei.fMask = SEE_MASK_INVOKEIDLIST
            sei.hwnd = None
            sei.lpVerb = "properties"
            sei.lpFile = path
            sei.nShow = 1

            ShellExecuteEx(ctypes.byref(sei))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open properties:\n{e}")


    # 🔁 Image Functions
    def rotate_clockwise(self):
        if self.original_image:
            self.original_image = self.original_image.rotate(-90, expand=True)
            self.save_image()
            self.fit_to_canvas()

    def rotate_counterclockwise(self):
        if self.original_image:
            self.original_image = self.original_image.rotate(90, expand=True)
            self.save_image()
            self.fit_to_canvas()

    def flip_horizontal(self):
        if self.original_image:
            self.original_image = ImageOps.mirror(self.original_image)
            self.save_image()
            self.fit_to_canvas()

    def flip_vertical(self):
        if self.original_image:
            self.original_image = ImageOps.flip(self.original_image)
            self.save_image()
            self.fit_to_canvas()

    def save_image(self):
        if self.original_image and self.image_paths:
            self.original_image.save(self.image_paths[self.current_index])

    def apply_file_filter(self, selected_ext):
        selected_ext = selected_ext.lower()
        self.active_ext_filter = None if selected_ext == "show all" else selected_ext

        if not self.full_image_list:
            return

        # Filter list
        filtered_list = [
            path for path in self.full_image_list
            if self.active_ext_filter is None or path.lower().endswith(self.active_ext_filter)
        ]

        self.image_paths = filtered_list

        if not self.image_paths:
            messagebox.showinfo("No Files", f"No files found with extension {selected_ext}")
            return

        self.current_index = 0
        self.show_image()

    # launch as import from anywhere

    def open_akas_converter(self):
        """Start akas_converter.py in a new Python process."""
        import subprocess, sys, os
        converter = os.path.join(os.path.dirname(__file__), "akas_converter.py")
        try:
            subprocess.Popen([sys.executable, converter])
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror(
                "Error",
                f"Could not launch AKAS Converter:\n{e}"
            )



        

    def delete_image(self, event=None):
        if self.image_paths:
            path = self.image_paths[self.current_index]
            try:
                send2trash(path)
                del self.image_paths[self.current_index]
                if not self.image_paths:
                    self.canvas.delete("all")
                    self.filename_label.config(text="")
                    self.image_info.config(text="")
                    return
                self.current_index = max(0, self.current_index - 1)
                self.show_image()
            except Exception as e:
                messagebox.showerror("Delete Failed", f"Could not delete file:\n{e}")

    def print_image(self):
        path = self.image_paths[self.current_index]
        if platform.system() == "Windows":
            os.startfile(path, "print")
        else:
            subprocess.run(["lp", path])

    def share_image(self):
        path = self.image_paths[self.current_index]
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
    def canvas_to_image_coords(self, x, y):
        cx, cy = self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2
        scale = self.fit_scale * self.zoom
        img_x = int((x - cx - self.pan_x) / scale)
        img_y = int((y - cy - self.pan_y) / scale)
        return img_x, img_y


    def on_canvas_click(self, event):
        if self.crop_mode:
            self.crop_start = (event.x, event.y)
        elif self.draw_mode:
            self.last_pan = (event.x, event.y)



    # 📂 Image Navigation & Zoom
    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*")])
        if not file_path:
            return

        folder_path = os.path.dirname(file_path)

        SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff",
                            ".ico", ".ppm", ".pgm", ".tga", ".dds", ".psd", ".psb", ".akas", ".pdf")

        # Get all valid files in same folder
        files = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(SUPPORTED_FORMATS):
                full_path = os.path.join(folder_path, filename)
                files.append(full_path)

        self.full_image_list = sorted(files)

        # Now apply the current filter (from dropdown)
        self.apply_file_filter(self.file_filter_var.get())

        # Set current index to the file user selected
        if file_path in self.image_paths:
            self.current_index = self.image_paths.index(file_path)
        else:
            self.current_index = 0  # fallback
        self.show_image()




    def open_bulk_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with Images")
        if not folder_path:
            return

        image_files = []
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename.lower().endswith(self.supported_exts):
                    full_path = os.path.join(root, filename)
                    image_files.append(full_path)

        if not image_files:
            messagebox.showinfo("No Files", "No supported image or PDF files found.")
            return

        self.full_image_list = sorted(image_files)
        self.apply_file_filter(self.file_filter_var.get())




    def load_image_from_path(self, file_path):
        folder = os.path.dirname(file_path)
        all_files = os.listdir(folder)
        self.image_paths = [
            os.path.join(folder, f)
            for f in all_files
            if f.lower().endswith(self.supported_exts)
        ]
        norm_path = os.path.normcase(os.path.abspath(file_path))
        self.image_paths = [os.path.normcase(os.path.abspath(p)) for p in self.image_paths]
        if norm_path in self.image_paths:
            self.current_index = self.image_paths.index(norm_path)
        else:
            self.current_index = 0
        self.show_image()

    def show_image(self):
        

        if hasattr(self, "after_id") and self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.akas_frames = []

        path = self.image_paths[self.current_index]
        ext = os.path.splitext(path)[1].lower()

        try:
            # ✅ Handle .akas files safely
            if ext == ".akas":
                # 🛑 Cancel any previous animation
                if hasattr(self, "after_id") and self.after_id:
                    self.root.after_cancel(self.after_id)
                    self.after_id = None
                self.akas_frames = []

                # Skip decoding if this file is already shown
                if hasattr(self, "akas_path") and self.akas_path == path:
                    return

                from akas_decoder import decode_akas
                result = decode_akas(path, save=False)

                if result is None or not isinstance(result, tuple) or len(result) != 2:
                    messagebox.showerror("Load Error", "❌ Invalid or unreadable .akas file.")
                    return

                metadata, frames = result
                if not frames:
                    messagebox.showerror("Load Error", "❌ No frames found in .akas file.")
                    return

                self.akas_frames = frames
                self.akas_path = path  # ✅ Remember current .akas file

                # ✅ Always show first frame
                self.original_image = frames[0][0]
                self.display_image()

                # ✅ Animate if multiple frames
                if len(frames) > 1:
                    self.animate_akas_frames(1)

                # ✅ Update UI title and label
                filename = os.path.basename(path)
                self.filename_label.config(text=f"{filename}   [{self.current_index+1}/{len(self.image_paths)}]")
                self.root.title(f"🖼️ AKAS - {filename}")

                return  # 🛑 Prevent fallthrough to Image.open

            elif ext == ".pdf":
                def get_poppler_path():
                    return str(Path(__file__).with_name("poppler") / "bin")

                poppler_path = get_poppler_path()
                self.pdf_pages = convert_from_path(path, poppler_path=poppler_path)

                if not self.pdf_pages:
                    raise ValueError("No pages returned from PDF.")

                self.pdf_page_index = 0
                self.pdf_path       = path
                self.original_image = self.pdf_pages[0]
                self.display_image()

                filename = os.path.basename(path)
                self.filename_label.config(
                    text=f"{filename} [Page 1/{len(self.pdf_pages)}]")

                return          # 🛑 stop here – do NOT fall through





            # ✅ Handle all other formats
            elif ext in (".psd", ".psb"):
                from psd_tools import PSDImage
                psd = PSDImage.open(path)
                preview = psd.composite()
                self.original_image = preview.convert("RGB")
            else:
                self.akas_path = None  # ✅ this is required
                self.original_image = Image.open(path)
                self.display_image()



            self.akas_path = None  # ✅ Reset if not .akas
            self.display_image()

        except Exception as e:
            messagebox.showerror("Load Error", f"Could not open image:\n{e}")

        path = self.image_paths[self.current_index]
        ext = os.path.splitext(path)[1].lower()

        try:
            if ext == ".akas":
                # Avoid re-decoding if already loaded
                if hasattr(self, "akas_path") and self.akas_path == path:
                    return  # Already shown

                self.akas_path = path  # Remember current akas path
                result = decode_akas(path, save=False)

                if result is None or not isinstance(result, tuple) or len(result) != 2:
                    messagebox.showerror("Load Error", "❌ Invalid or unreadable .akas file.")
                    return

                metadata, frames = result
                if not frames:
                    messagebox.showerror("Load Error", "❌ No frames found in .akas file.")
                    return

                self.akas_frames = frames

                if len(frames) > 1:
                    self.original_image = frames[0][0]
                    self.animate_akas_frames(0)
                else:
                    self.original_image = frames[0][0]
                    self.display_image()
                return  # ✅ Prevent fall-through


            elif ext in (".psd", ".psb"):
                from psd_tools import PSDImage
                psd = PSDImage.open(path)
                preview = psd.composite()
                self.original_image = preview.convert("RGB")

            else:
                self.original_image = Image.open(path)

            self.display_image()

        except Exception as e:
            messagebox.showerror("Load Error", f"Could not open image:\n{e}")

        path = self.image_paths[self.current_index]
        ext = os.path.splitext(path)[1].lower()

        try:
            if ext == ".akas":
                result = decode_akas(path, save=False)

                if result is None or not isinstance(result, tuple) or len(result) != 2:
                    messagebox.showerror("Load Error", "❌ Invalid or unreadable .akas file.")
                    return

                metadata, frames = result
                if not frames:
                    messagebox.showerror("Load Error", "❌ No frames found in .akas file.")
                    return

                self.akas_frames = frames

                if len(frames) > 1:
                    self.animate_akas_frames(0)
                else:
                    self.original_image = frames[0][0]
                    self.update_view(path)
                return  # Don't continue past this point

            elif ext in (".psd", ".psb"):
                from psd_tools import PSDImage
                psd = PSDImage.open(path)
                preview = psd.composite()
                self.original_image = preview.convert("RGB")

            else:
                self.original_image = Image.open(path)

            self.update_view(path)

        except Exception as e:
            messagebox.showerror("Load Error", f"Could not open image:\n{e}")

    def fit_to_canvas(self):
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        iw, ih = self.original_image.size
        self.fit_scale = min(cw / iw, ch / ih, 1.0)
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.display_image()
        

    def animate_akas_frames(self, index=0):
        # 🛡️ Check if frames exist
        if not hasattr(self, "akas_frames") or not self.akas_frames:
            return

        # 🛡️ Double-check we're still on the same .akas file
        if not hasattr(self, "akas_path") or self.image_paths[self.current_index] != self.akas_path:
            return

        img, duration = self.akas_frames[index]
        self.original_image = img
        self.display_image()

        next_index = (index + 1) % len(self.akas_frames)
        self.after_id = self.root.after(duration, lambda: self.animate_akas_frames(next_index))







    def display_image(self):
        # ✅ Prevent crash if image not loaded
        if not hasattr(self, 'original_image') or self.original_image is None:
            print("⚠️ No image loaded, skipping display_image()")
            return

        scale = self.fit_scale * self.zoom
        iw, ih = self.original_image.size
        new_w, new_h = int(iw * scale), int(ih * scale)
        img = self.original_image.resize((new_w, new_h), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        cx, cy = self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2
        self.canvas.create_image(cx + self.pan_x, cy + self.pan_y, image=self.tk_image)
        percent = int(self.fit_scale * self.zoom * 100)
        self.zoom_label.config(text=f"{percent}%")
        if self.zoom_slider.get() != percent:
            self.zoom_slider.set(percent)



    def slider_zoom(self, val):
        percent = int(val)
        self.zoom = percent / 100 / self.fit_scale
        self.zoom = max(1.0, min(self.zoom, 2.0 / self.fit_scale))
        self.display_image()

    def adjust_zoom(self, factor):
        new_zoom = self.zoom * factor
        self.zoom = max(1.0, min(new_zoom, 2.0 / self.fit_scale))
        self.display_image()

    def double_click_zoom(self, event=None):
        if self.zoom <= 1.0:
            self.zoom = 2.0 / self.fit_scale
        else:
            self.zoom = 1.0
            self.pan_x = 0
            self.pan_y = 0
        self.display_image()

    def update_view(self, path):
        filename = os.path.basename(path)
        self.filename_label.config(text=f"{filename}   [{self.current_index+1}/{len(self.image_paths)}]")
        self.root.title(f"🖼️ AKAS - {filename}")
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.root.after(100, self.fit_to_canvas)

        if hasattr(self, "original_image"):
            w, h = self.original_image.size
            size_kb = os.path.getsize(path) / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
            self.image_info.config(text=f"{w}x{h}px | {size_str}")


    def pan_start(self, event):
        self.last_pan = (event.x, event.y)

    def pan_move(self, event):
        if self.last_pan:
            dx = event.x - self.last_pan[0]
            dy = event.y - self.last_pan[1]
            self.pan_x += dx
            self.pan_y += dy
            self.last_pan = (event.x, event.y)
            self.display_image()

    def on_resize(self, event=None):
        if self.original_image:
            self.fit_to_canvas()

    def mouse_zoom(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.adjust_zoom(factor)

    
    '''
    def prev_image(self):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.show_image()

    def next_image(self):
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.show_image()
    '''
    def activate_crop(self):
        self.crop_mode = True
        self.crop_start = None
        self.canvas.config(cursor="cross")
    
    def next_image(self):
    # ✅ PDF: go to next page if available
        if self.pdf_pages and self.pdf_page_index < len(self.pdf_pages) - 1:
            self.pdf_page_index += 1
            self.original_image = self.pdf_pages[self.pdf_page_index]
            self.display_image()
            filename = os.path.basename(self.pdf_path)
            self.filename_label.config(text=f"{filename} [Page {self.pdf_page_index + 1}/{len(self.pdf_pages)}]")
            self.root.title(f"📄 PDF - {filename}")
            return

        # ✅ Default next image
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.show_image()

    def prev_image(self):
        # ✅ PDF: go to previous page if available
        if self.pdf_pages and self.pdf_page_index > 0:
            self.pdf_page_index -= 1
            self.original_image = self.pdf_pages[self.pdf_page_index]
            self.display_image()
            filename = os.path.basename(self.pdf_path)
            self.filename_label.config(text=f"{filename} [Page {self.pdf_page_index + 1}/{len(self.pdf_pages)}]")
            self.root.title(f"📄 PDF - {filename}")
            return

        # ✅ Default previous image
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.show_image()

    def resize_image_popup(self):
        if not self.original_image:
            return
        popup = Toplevel(self.root)
        popup.title("Resize Image")

        Label(popup, text="Width:").pack()
        width_entry = Entry(popup)
        width_entry.insert(0, str(self.original_image.width))
        width_entry.pack()

        Label(popup, text="Height:").pack()
        height_entry = Entry(popup)
        height_entry.insert(0, str(self.original_image.height))
        height_entry.pack()

        def apply_resize():
            try:
                w = int(width_entry.get())
                h = int(height_entry.get())
                self.original_image = self.original_image.resize((w, h), Image.LANCZOS)
                self.fit_to_canvas()
                popup.destroy()
            except:
                messagebox.showerror("Invalid Input", "Please enter valid numbers.")

        Button(popup, text="Apply", command=apply_resize).pack()

    def show_filter_menu(self):
        if not self.original_image:
            return
        menu = Menu(self.root, tearoff=0)
        menu.add_command(label="Grayscale", command=self.apply_grayscale)
        menu.add_command(label="Sepia", command=self.apply_sepia)
        menu.add_command(label="Invert", command=self.apply_invert)
        menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def apply_grayscale(self):
        self.original_image = ImageOps.grayscale(self.original_image).convert("RGB")
        self.fit_to_canvas()

    def apply_sepia(self):
        img = self.original_image.convert("RGB")
        sepia = Image.new("RGB", img.size)
        pixels = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = pixels[x, y]
                tr = int(0.393*r + 0.769*g + 0.189*b)
                tg = int(0.349*r + 0.686*g + 0.168*b)
                tb = int(0.272*r + 0.534*g + 0.131*b)
                sepia.putpixel((x, y), (min(tr,255), min(tg,255), min(tb,255)))
        self.original_image = sepia
        self.fit_to_canvas()

    def apply_invert(self):
        self.original_image = ImageOps.invert(self.original_image.convert("RGB"))
        self.fit_to_canvas()

    def toggle_draw_mode(self):
        self.draw_mode = not self.draw_mode
        self.canvas.config(cursor="pencil" if self.draw_mode else "fleur")

    def add_text_popup(self):
        popup = Toplevel(self.root)
        popup.title("Add Text")

        Label(popup, text="Enter text:").pack()
        text_entry = Entry(popup)
        text_entry.pack()

        def place_text():
            text = text_entry.get()
            if not text:
                return
            popup.destroy()

            def on_click(event):
                draw = ImageDraw.Draw(self.original_image)
                font = ImageFont.load_default()
                draw.text((event.x, event.y), text, fill=(255, 0, 0), font=font)
                self.canvas.unbind("<Button-1>")
                self.fit_to_canvas()

            self.canvas.bind("<Button-1>", on_click)

        Button(popup, text="OK", command=place_text).pack()

    def toggle_dark_light(self):
        self.dark_mode = not self.dark_mode
        bg = "#ffffff" if not self.dark_mode else "#121212"
        fg = "#000000" if not self.dark_mode else "#eeeeee"
        self.root.configure(bg=bg)
        self.topbar.configure(bg=bg)
        self.canvas.configure(bg=bg)
        self.bottombar.configure(bg=bg)
        self.filename_label.configure(bg=bg, fg=fg)
        self.zoom_label.configure(bg=bg, fg=fg)
        self.image_info.configure(bg=bg, fg=fg)


    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)


    def on_canvas_drag(self, event):
        if hasattr(self, "crop_mode") and self.crop_mode and self.crop_start:
            self.canvas.delete("crop_rect")
            self.canvas.create_rectangle(self.crop_start[0], self.crop_start[1], event.x, event.y, outline="red", tag="crop_rect")
        elif hasattr(self, "draw_mode") and self.draw_mode and self.last_pan:
            x1, y1 = self.last_pan
            x2, y2 = event.x, event.y
            draw = ImageDraw.Draw(self.original_image)
            draw.line([x1, y1, x2, y2], fill="red", width=2)
            self.last_pan = (x2, y2)
            self.fit_to_canvas()

    def on_canvas_release(self, event):
        if self.crop_mode and self.crop_start:
            x1, y1 = self.crop_start
            x2, y2 = event.x, event.y

            # Convert canvas coordinates to image coordinates
            cx, cy = self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2
            scale = self.fit_scale * self.zoom

            img_x1 = int((x1 - cx - self.pan_x) / scale)
            img_y1 = int((y1 - cy - self.pan_y) / scale)
            img_x2 = int((x2 - cx - self.pan_x) / scale)
            img_y2 = int((y2 - cy - self.pan_y) / scale)

            box = (min(img_x1, img_x2), min(img_y1, img_y2), max(img_x1, img_x2), max(img_y1, img_y2))
            try:
                self.original_image = self.original_image.crop(box)
                self.crop_mode = False
                self.canvas.config(cursor="fleur")
                self.fit_to_canvas()
            except Exception as e:
                messagebox.showerror("Crop Failed", str(e))



if __name__ == "__main__":
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    MaayraImageViewer(file_arg)
    