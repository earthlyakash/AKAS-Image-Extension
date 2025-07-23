import os, mimetypes, tkinter as tk
from tkinter import filedialog
from PIL import Image
from akas_encoder import encode_image, encode_video
from akas_decoder import decode_akas

def is_video_file(path):
    mime = mimetypes.guess_type(path)[0]
    return mime and mime.startswith("video")

def is_animated_gif(path):
    try:
        return getattr(Image.open(path), "is_animated", False)
    except Exception:
        return False

def to_akas(path, out_dir, log, quality):
    name, ext = os.path.splitext(os.path.basename(path))
    ext = ext.lower()
    meta = {"creator": "Akash Kumar", "source_file": path}
    q = int(quality * 10)

    try:
        if ext == ".gif" and is_animated_gif(path):
            out = os.path.join(out_dir, f"{name}_ani.akas")
            encode_image(path, out, meta, quality=q)

        elif is_video_file(path):
            out = os.path.join(out_dir, f"{name}_ani.akas")
            encode_video(path, out, meta, quality=q)

        elif ext != ".akas":
            out = os.path.join(out_dir, f"{name}.akas")
            encode_image(path, out, meta, quality=q)

        log.insert(tk.END, f"✅ Converted to: {os.path.basename(out)}\n")
    except Exception as e:
        log.insert(tk.END, f"❌ Failed to convert to .akas: {e}\n")

def from_akas(path, out_dir, log, selected_format):
    name, ext = os.path.splitext(os.path.basename(path))
    ext = ext.lower()

    try:
        if ext != ".akas":
            raise Exception("Not a .akas file")

        meta_out, frames = decode_akas(path, save=False)
        if not frames:
            raise Exception("No frames decoded")

        selected_format = selected_format.lower().strip(".")

        if selected_format == "gif" and len(frames) > 1:
            imgs = [f[0].convert("RGBA") for f in frames]
            durs = [f[1] for f in frames]
            out = os.path.join(out_dir, f"{name}.gif")
            imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=durs, loop=0)
        else:
            img = frames[0][0].convert("RGBA")
            out = os.path.join(out_dir, f"{name}.{selected_format}")
            if selected_format in ("jpg", "jpeg", "bmp"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1])
                bg.save(out)
            else:
                img.save(out)

        log.insert(tk.END, f"✅ Converted to: {os.path.basename(out)}\n")
    except Exception as e:
        log.insert(tk.END, f"❌ Failed: {e}\n")

def launch_gui():
    root = tk.Tk()
    root.title("🖼️ AKASH File Converter")
    root.geometry("880x500")
    root.configure(bg="#f0f0f0")

    title = tk.Label(root, text="🔄 AKASH Format Converter", font=("Arial", 20, "bold"), bg="#f0f0f0")
    title.pack(pady=10)

    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(fill="both", expand=True, padx=10)

    # LEFT PANEL
    left = tk.LabelFrame(frame, text="📤 Convert TO .akas", font=("Arial", 12, "bold"), width=400, bg="#ffffff")
    left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    log1 = tk.Text(left, height=16, width=50, bg="#fefefe")
    log1.pack(pady=10)

    q_label = tk.Label(left, text="Compression Quality (1–10):", bg="#ffffff")
    q_label.pack()
    q_val = tk.IntVar(value=6)
    tk.Scale(left, from_=1, to=10, orient="horizontal", variable=q_val, bg="#ffffff").pack()

    def single_to_akas():
        p = filedialog.askopenfilename(title="Select image / video")
        if p:
            to_akas(p, os.path.dirname(p), log1, q_val.get())

    def bulk_to_akas():
        d = filedialog.askdirectory(title="Select folder with images / videos")
        if not d: return
        out_d = d.rstrip("/\\") + "_akas"
        os.makedirs(out_d, exist_ok=True)

        valid = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff", ".avif", ".gif", ".mp4", ".mov", ".avi", ".mkv"}
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if os.path.isfile(p) and os.path.splitext(f)[1].lower() in valid:
                to_akas(p, out_d, log1, q_val.get())

        log1.insert(tk.END, f"\n✅ All saved to: {out_d}\n")

    tk.Button(left, text="Convert Single File", command=single_to_akas, width=32).pack(pady=4)
    tk.Button(left, text="Convert Folder (Bulk)", command=bulk_to_akas, width=32).pack(pady=4)

    # RIGHT PANEL
    right = tk.LabelFrame(frame, text="📥 Convert FROM .akas", font=("Arial", 12, "bold"), width=400, bg="#ffffff")
    right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    log2 = tk.Text(right, height=16, width=50, bg="#fefefe")
    log2.pack(pady=10)

    format_label = tk.Label(right, text="Convert to format:", bg="#ffffff", font=("Arial", 10))
    format_label.pack()

    format_var = tk.StringVar(value="png")
    format_options = [".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff", ".avif", ".gif"]
    format_menu = tk.OptionMenu(right, format_var, *format_options)
    format_menu.pack(pady=4)

    def single_from_akas():
        p = filedialog.askopenfilename(title="Select .akas file")
        if p:
            from_akas(p, os.path.dirname(p), log2, format_var.get())

    def bulk_from_akas():
        d = filedialog.askdirectory(title="Select folder with .akas files")
        if not d: return
        out_d = d.rstrip("/\\") + "_converted"
        os.makedirs(out_d, exist_ok=True)

        for f in os.listdir(d):
            p = os.path.join(d, f)
            if os.path.isfile(p) and os.path.splitext(f)[1].lower() == ".akas":
                from_akas(p, out_d, log2, format_var.get())

        log2.insert(tk.END, f"\n✅ All saved to: {out_d}\n")

    tk.Button(right, text="Convert Single .akas", command=single_from_akas, width=32).pack(pady=4)
    tk.Button(right, text="Convert Folder (Bulk)", command=bulk_from_akas, width=32).pack(pady=4)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()
