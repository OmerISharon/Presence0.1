import subprocess
import tkinter as tk
from tkinter import filedialog, colorchooser, ttk, messagebox
from pathlib import Path
import sys

# Path to the Picasso CLI script (adjust if necessary)
PICASSO_SCRIPT = Path(__file__).parent / "picasso_v1.py"

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def pick_file(initial=".", filetypes=(("All files", "*.*"),)):
    return filedialog.askopenfilename(initialdir=initial, filetypes=filetypes)

def pick_color(initial="#ffffff"):
    col = colorchooser.askcolor(initialcolor=initial)
    if col[1]:
        rgb = col[0]
        return f"{int(rgb[0])},{int(rgb[1])},{int(rgb[2])}"
    return None

# ---------------------------------------------------------------------------
# Main GUI class
# ---------------------------------------------------------------------------

class PicassoGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Picasso 4K Image Generator")
        self.geometry("700x650")
        self.configure(padx=10, pady=10)

        self._build_widgets()

    # ----------------------- UI Layout ------------------------------------
    def _build_widgets(self):
        # text
        tk.Label(self, text="Quote / Text:").grid(row=0, column=0, sticky="w")
        self.text_entry = tk.Text(self, height=4, width=60)
        self.text_entry.grid(row=0, column=1, columnspan=3, sticky="we")
        self.text_entry.insert("1.0", "Your presence is the power you’ve been seeking")

        # output path
        tk.Label(self, text="Output file:").grid(row=1, column=0, sticky="w")
        self.out_var = tk.StringVar(value=fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules\creators\picasso\picasso_v1\test_output\test_output.jpg")
        tk.Entry(self, textvariable=self.out_var, width=50).grid(row=1, column=1, sticky="we")
        tk.Button(self, text="Browse", command=self._browse_output).grid(row=1, column=2)

        # orientation
        tk.Label(self, text="Orientation:").grid(row=2, column=0, sticky="w")
        self.orientation_var = tk.StringVar(value="vertical")
        ttk.Combobox(self, textvariable=self.orientation_var, values=["square", "vertical", "horizontal"], width=15).grid(row=2, column=1, sticky="w")

        # media path
        tk.Label(self, text="Background image:").grid(row=3, column=0, sticky="w")
        self.media_var = tk.StringVar(value=fr"D:\2025\Projects\Presence\Presence0.1\Resources\Media_Resources\Image\Vertical\Animal\pexels-markb-106685\pexels-markb-106685.jpg")
        tk.Entry(self, textvariable=self.media_var, width=50).grid(row=3, column=1, sticky="we")
        tk.Button(self, text="Browse", command=self._browse_media).grid(row=3, column=2)

        # font size level
        tk.Label(self, text="Font size level:").grid(row=4, column=0, sticky="w")
        self.font_size_var = tk.StringVar(value="medium")
        ttk.Combobox(self, textvariable=self.font_size_var, values=["tiny", "small", "medium", "large", "big"], width=15).grid(row=4, column=1, sticky="w")

        # alignments
        tk.Label(self, text="H Align:").grid(row=5, column=0, sticky="w")
        self.halign_var = tk.StringVar(value="center")
        ttk.Combobox(self, textvariable=self.halign_var, values=["left", "center", "right"], width=10).grid(row=5, column=1, sticky="w")
        tk.Label(self, text="V Align:").grid(row=5, column=2, sticky="w")
        self.valign_var = tk.StringVar(value="center")
        ttk.Combobox(self, textvariable=self.valign_var, values=["top", "center", "bottom"], width=10).grid(row=5, column=3, sticky="w")

        # colors
        tk.Label(self, text="Text color:").grid(row=6, column=0, sticky="w")
        self.fore_var = tk.StringVar(value="0,0,0")
        tk.Entry(self, textvariable=self.fore_var, width=20).grid(row=6, column=1, sticky="w")
        tk.Button(self, text="Pick", command=lambda: self._pick_color(self.fore_var)).grid(row=6, column=2)

        tk.Label(self, text="BG color:").grid(row=7, column=0, sticky="w")
        self.bg_var = tk.StringVar(value="255,255,255")
        tk.Entry(self, textvariable=self.bg_var, width=20).grid(row=7, column=1, sticky="w")
        tk.Button(self, text="Pick", command=lambda: self._pick_color(self.bg_var)).grid(row=7, column=2)

        # effects
        self.effects_frame = tk.LabelFrame(self, text="Font Effects")
        self.effects_frame.grid(row=8, column=0, columnspan=4, sticky="we", pady=10)
        self.stroke_chk = tk.IntVar()
        self.shadow_chk = tk.IntVar()
        self.marker_chk = tk.IntVar()
        self.fade_chk = tk.IntVar()
        tk.Checkbutton(self.effects_frame, text="Stroke", variable=self.stroke_chk).grid(row=0, column=0, sticky="w")
        tk.Checkbutton(self.effects_frame, text="Shadow", variable=self.shadow_chk).grid(row=0, column=1, sticky="w")
        tk.Checkbutton(self.effects_frame, text="Marker", variable=self.marker_chk).grid(row=0, column=2, sticky="w")
        tk.Checkbutton(self.effects_frame, text="Fade", variable=self.fade_chk).grid(row=0, column=3, sticky="w")

        # fade strength
        tk.Label(self.effects_frame, text="Fade strength (0-1):").grid(row=1, column=0, sticky="e")
        self.fade_str_var = tk.DoubleVar(value=0.2)
        tk.Entry(self.effects_frame, textvariable=self.fade_str_var, width=6).grid(row=1, column=1, sticky="w")

        # stroke / shadow / marker colors
        tk.Label(self.effects_frame, text="Stroke color RGBA:").grid(row=2, column=0, sticky="e")
        self.stroke_col_var = tk.StringVar(value="255,255,255,255")
        tk.Entry(self.effects_frame, textvariable=self.stroke_col_var, width=20).grid(row=2, column=1)

        tk.Label(self.effects_frame, text="Shadow color RGBA:").grid(row=2, column=2, sticky="e")
        self.shadow_col_var = tk.StringVar(value="0,0,0,120")
        tk.Entry(self.effects_frame, textvariable=self.shadow_col_var, width=20).grid(row=2, column=3)

        tk.Label(self.effects_frame, text="Marker color RGBA:").grid(row=3, column=0, sticky="e")
        self.marker_col_var = tk.StringVar(value="255,255,255,180")
        tk.Entry(self.effects_frame, textvariable=self.marker_col_var, width=20).grid(row=3, column=1)

        tk.Label(self.effects_frame, text="Fade target RGBA:").grid(row=3, column=2, sticky="e")
        self.fade_col_var = tk.StringVar(value="255,255,255,255")
        tk.Entry(self.effects_frame, textvariable=self.fade_col_var, width=20).grid(row=3, column=3)

        # Border section
        border_frame = tk.LabelFrame(self, text="Border")
        border_frame.grid(row=9, column=0, columnspan=4, sticky="we")
        tk.Label(border_frame, text="Effect:").grid(row=0, column=0, sticky="w")
        self.border_eff_var = tk.StringVar(value="")
        ttk.Combobox(border_frame, textvariable=self.border_eff_var, values=["", "simple", "rounded_corners", "glow"], width=15).grid(row=0, column=1)
        tk.Label(border_frame, text="Width:").grid(row=0, column=2)
        self.border_width_var = tk.IntVar(value=40)
        tk.Entry(border_frame, textvariable=self.border_width_var, width=6).grid(row=0, column=3)
        tk.Label(border_frame, text="Color RGBA:").grid(row=1, column=0, sticky="e")
        self.border_col_var = tk.StringVar(value="255,255,255,128")
        tk.Entry(border_frame, textvariable=self.border_col_var, width=20).grid(row=1, column=1)

        # Overlay filters
        overlay_frame = tk.LabelFrame(self, text="Image Overlay ('blur', 'darken', 'brighten', 'color_tint')")
        overlay_frame.grid(row=10, column=0, columnspan=4, sticky="we", pady=10)
        tk.Label(overlay_frame, text="Effects (comma):").grid(row=0, column=0, sticky="w")
        self.overlay_eff_var = tk.StringVar()
        tk.Entry(overlay_frame, textvariable=self.overlay_eff_var, width=30).grid(row=0, column=1, columnspan=2, sticky="we")
        tk.Label(overlay_frame, text="Tint RGBA:").grid(row=1, column=0, sticky="w")
        self.overlay_tint_var = tk.StringVar(value="255,255,255,50")
        tk.Entry(overlay_frame, textvariable=self.overlay_tint_var, width=20).grid(row=1, column=1)
        tk.Label(overlay_frame, text="Blur radius:").grid(row=1, column=2, sticky="e")
        self.blur_var = tk.IntVar(value=5)
        tk.Entry(overlay_frame, textvariable=self.blur_var, width=6).grid(row=1, column=3, sticky="w")

        # Run button
        tk.Button(self, text="Generate Image", bg="#4caf50", fg="white", command=self.run_picasso).grid(row=11, column=0, columnspan=4, pady=20, ipadx=10, ipady=5)

    # ----------------------- Callbacks ------------------------------------
    def _browse_output(self):
        file = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=(("JPEG", "*.jpg"),))
        if file:
            self.out_var.set(file)

    def _browse_media(self):
        file = pick_file(filetypes=(("Images", "*.jpg;*.png;*.jpeg"),))
        if file:
            self.media_var.set(file)

    def _pick_color(self, var):
        col = pick_color()
        if col:
            var.set(col)

    # ----------------------- Run generator --------------------------------
    def run_picasso(self):
        if not self.out_var.get():
            messagebox.showerror("Missing", "Please choose an output path")
            return

        effects = []
        if self.stroke_chk.get():
            effects.append("stroke")
        if self.shadow_chk.get():
            effects.append("shadow")
        if self.marker_chk.get():
            effects.append("marker")
        if self.fade_chk.get():
            effects.append("fade")
        eff_str = ",".join(effects)

        cmd = [sys.executable, str(PICASSO_SCRIPT),
               "--text", self.text_entry.get("1.0", "end").strip(),
               "--output_path", self.out_var.get(),
               "--image_orientation", self.orientation_var.get(),
               "--fore_color", self.fore_var.get(),
               "--bg_color", self.bg_var.get(),
               "--font_size", self.font_size_var.get(),
               "--text_h_align", self.halign_var.get(),
               "--text_v_align", self.valign_var.get(),
               "--font_effect", eff_str,
               "--font_stroke_effect_color", self.stroke_col_var.get(),
               "--font_shadow_effect_color", self.shadow_col_var.get(),
               "--font_marker_effect_color", self.marker_col_var.get(),
               "--font_fade_effect_color", self.fade_col_var.get(),
               "--font_fade_effect_strength", str(self.fade_str_var.get()),
               "--border_effect", self.border_eff_var.get(),
               "--border_width", str(self.border_width_var.get()),
               "--border_effect_color", self.border_col_var.get(),
               "--image_overlay_effect", self.overlay_eff_var.get(),
               "--image_overlay_effect_tint_color", self.overlay_tint_var.get(),
               "--blur_amount", str(self.blur_var.get())]

        if self.media_var.get():
            cmd.extend(["--media_path", self.media_var.get()])

        try:
            subprocess.run(cmd, check=True)
            messagebox.showinfo("Success", "Image generated successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to generate image\n{e}")


if __name__ == "__main__":
    app = PicassoGUI()
    app.mainloop()
