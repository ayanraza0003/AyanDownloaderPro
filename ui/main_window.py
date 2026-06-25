from backend.preview import PreviewManager
import customtkinter as ctk
from tkinter import filedialog
import threading, time, os
from backend.thumbnail import ThumbnailManager
from PIL import ImageTk
# ---------- THEME ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
# Palette
BG          = "#0B0D12"   # deep charcoal
SURFACE     = "#12151C"   # card base
SURFACE_2   = "#171B24"   # elevated
SURFACE_3   = "#1E232E"   # hover / input
BORDER      = "#262C38"
BORDER_SOFT = "#1B2029"
TEXT        = "#EDEFF4"
TEXT_DIM    = "#9AA3B2"
TEXT_MUTED  = "#5C6473"
ACCENT      = "#3B82F6"   # electric blue
ACCENT_HOV  = "#2563EB"
ACCENT_GLOW = "#60A5FA"
PURPLE      = "#8B5CF6"
SUCCESS     = "#10B981"
SUCCESS_HOV = "#059669"
FONT_FAMILY = "Segoe UI Variable"  # Win11; CTk falls back if absent
# ---------- HELPERS ----------
def f(size, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)
# ---------- APP ----------
class AyanDownloaderPro(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG)
        self.title("Ayan Downloader Pro")
        self.geometry("1000x700")
        self.minsize(1000, 700)
        self._center()
        self.mode = ctk.StringVar(value="video")
        self.folder = ctk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.url_var = ctk.StringVar()
        self.preview_manager = PreviewManager()
        self.thumbnail_manager = ThumbnailManager()
        self.preview_after_id = None
        self.selected_quality = None
        self._build_header()
        self._build_main()
        self._build_footer()

    def _center(self):
        self.update_idletasks()
        w, h = 1000, 700
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
    # =================== HEADER ===================
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=92)
        header.pack(fill="x", padx=28, pady=(22, 6))
        header.pack_propagate(False)
        # Logo tile
        logo = ctk.CTkFrame(header, width=56, height=56, corner_radius=16,
                            fg_color=ACCENT, border_width=0)
        logo.pack(side="left", padx=(0, 16))
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="⚡", font=f(28, "bold"),
                     text_color="#FFFFFF").pack(expand=True)
        text_wrap = ctk.CTkFrame(header, fg_color="transparent")
        text_wrap.pack(side="left", anchor="w")
        ctk.CTkLabel(text_wrap, text="AYAN DOWNLOADER PRO",
                     font=f(24, "bold"), text_color=TEXT
                     ).pack(anchor="w")
        ctk.CTkLabel(text_wrap, text="Fast  •  High Quality  •  Audio & Video",
                     font=f(13), text_color=TEXT_DIM
                     ).pack(anchor="w", pady=(2, 1))
        ctk.CTkLabel(text_wrap, text="Powered by yt-dlp + FFmpeg",
                     font=f(11), text_color=TEXT_MUTED
                     ).pack(anchor="w")
        # Window pill (right side decorative)
        pill = ctk.CTkFrame(header, fg_color=SURFACE_2, corner_radius=999,
                            border_width=1, border_color=BORDER, height=34)
        pill.pack(side="right", pady=10)
        ctk.CTkLabel(pill, text="●  Ready", font=f(12, "bold"),
                     text_color=SUCCESS).pack(padx=14, pady=6)
    # =================== MAIN CARD ===================
    def _build_main(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                        scrollbar_button_color=SURFACE_3,
                                        scrollbar_button_hover_color=BORDER)
        scroll.pack(fill="both", expand=True, padx=28, pady=(6, 6))
        card = ctk.CTkFrame(scroll, fg_color=SURFACE, corner_radius=20,
                            border_width=1, border_color=BORDER_SOFT)
        card.pack(fill="x", padx=2, pady=2)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=26, pady=24)
        self._section_url(inner)
        self._section_preview(inner)
        self._section_mode(inner)
        self._section_folder(inner)
        self._section_download_btn(inner)
        self._section_progress(inner)
    # ---- URL ----
    def _section_url(self, parent):
        ctk.CTkLabel(parent, text="Paste Video URL",
                     font=f(13, "bold"), text_color=TEXT_DIM
                     ).pack(anchor="w", pady=(0, 8))
        box = ctk.CTkFrame(parent, fg_color=SURFACE_2, corner_radius=14,
                           border_width=1, border_color=BORDER, height=56)
        box.pack(fill="x")
        box.pack_propagate(False)
        entry = ctk.CTkEntry(box, textvariable=self.url_var,
                             placeholder_text="Paste YouTube URL here…",
                             font=f(14), text_color=TEXT,
                             placeholder_text_color=TEXT_MUTED,
                             fg_color="transparent", border_width=0, height=54)
        entry.pack(side="left", fill="both", expand=True, padx=(18, 8))
        entry.bind("<Return>", lambda e: self.load_preview(self.url_var.get()))
        entry.bind("<KeyRelease>", self._schedule_preview)
        paste_btn = ctk.CTkButton(box, text="📋  Paste", width=110, height=38,
                                  corner_radius=10, font=f(12, "bold"),
                                  fg_color=SURFACE_3, hover_color=BORDER,
                                  text_color=TEXT, command=self._paste)
        paste_btn.pack(side="right", padx=10)

    def _paste(self):
        try:
            url = self.clipboard_get().strip()
            self.url_var.set(url)

            if self.preview_after_id:
                self.after_cancel(self.preview_after_id)

            self.load_preview(url)

        except Exception:
            pass

    def load_preview(self, url):
        if not url:
            self.title_lbl.configure(text="Paste a link to preview your media")
            self.meta_lbl.configure(text="Channel • Duration • Views")

            for widget in self.chips.winfo_children():
                widget.destroy()
            self.thumbnail = None
            self.thumb_label.configure(image=None, text="▶")
            return

        info = self.preview_manager.get_info(url)

        if "error" in info:
            self.title_lbl.configure(text="Invalid URL")
            self.meta_lbl.configure(text=info["error"])
            return

        self.title_lbl.configure(text=info["title"])

        self.meta_lbl.configure(
            text=f'{info["channel"]} • {info["duration"]} sec • {info["views"]:,} views'
        )
        for widget in self.chips.winfo_children():
            widget.destroy()

        self.quality_chips = []

        if self.mode.get() == "audio":
            chip = ctk.CTkFrame(
                self.chips,
                fg_color=ACCENT,
                corner_radius=999,
                border_width=1,
                border_color=ACCENT,
            )
            chip.pack(side="left", padx=(0, 6))

            ctk.CTkLabel(
                chip,
                text="Best MP3",
                font=f(11, "bold"),
                text_color="#FFFFFF",
            ).pack(padx=10, pady=3)

            self.selected_quality = "bestaudio"

        else:
            for quality in info["qualities"]:
                chip = ctk.CTkFrame(
                self.chips,
                fg_color=SURFACE_3,
                corner_radius=999,
                border_width=1,
                border_color=BORDER,
                cursor="hand2"
                )
                chip.pack(side="left", padx=(0, 6))

                label = ctk.CTkLabel(
                chip,
                text=quality,
                font=f(11, "bold"),
                text_color=TEXT_DIM
                )
                label.pack(padx=10, pady=3)

                chip.bind("<Button-1>", lambda e, q=quality: self.select_quality(q))
                label.bind("<Button-1>", lambda e, q=quality: self.select_quality(q))

                self.quality_chips.append((chip, quality))
        if info["qualities"]:
            self.select_quality(info["qualities"][0])

        try:
            print("Loading thumbnail...")
            image = self.thumbnail_manager.get_image(info["thumbnail"]).copy()
            image = image.resize((180, 104))

            self.thumbnail = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(180, 104)
            )

            # Step 1: clear the label so Tkinter sees a real state change
            self.thumb_label.configure(image=None, text="")
            # Step 2: apply the new image on the next event-loop tick
            self.after(0, lambda img=self.thumbnail: self.thumb_label.configure(
                text="", image=img
            ))
            print("Thumbnail applied")
        except Exception as e:
            print(f"Thumbnail Error: {e}")

    def _schedule_preview(self, event=None):
        if self.preview_after_id:
            self.after_cancel(self.preview_after_id)

        self.preview_after_id = self.after(
            800,
            lambda: self.load_preview(self.url_var.get().strip())
        )

    # ---- Preview ----
    def _section_preview(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color=SURFACE_2, corner_radius=16,
                            border_width=1, border_color=BORDER, height=128)
        wrap.pack(fill="x", pady=(16, 0))
        wrap.pack_propagate(False)
        thumb = ctk.CTkFrame(wrap, width=180, height=104, corner_radius=12,
                             fg_color=ACCENT)
        thumb.pack(side="left", padx=12, pady=12)
        thumb.pack_propagate(False)
        self.thumb_label = ctk.CTkLabel(thumb, text="", text_color="#FFFFFF")
        self.thumb_label.pack(expand=True, fill="both")
        info = ctk.CTkFrame(wrap, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=(6, 16), pady=14)
        self.title_lbl = ctk.CTkLabel(info, text="Paste a link to preview your media",
                 font=f(15, "bold"), text_color=TEXT
                 )
        self.title_lbl.pack(anchor="w")
        self.meta_lbl = ctk.CTkLabel(info, text="Channel  •  Duration  •  Views",
                     font=f(12), text_color=TEXT_DIM
                     )
        self.meta_lbl.pack(anchor="w", pady=(4, 10))
        self.chips = ctk.CTkFrame(info, fg_color="transparent")
        self.chips.pack(anchor="w")
    # ---- Mode cards ----
    def _section_mode(self, parent):
        ctk.CTkLabel(parent, text="Download Mode",
                     font=f(13, "bold"), text_color=TEXT_DIM
                     ).pack(anchor="w", pady=(20, 8))
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x")
        row.grid_columnconfigure((0, 1), weight=1, uniform="m")
        self.card_video = self._mode_card(
            row, "🎥", "Best Video",
            "Highest quality video with audio", "video")
        self.card_video.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.card_audio = self._mode_card(
            row, "🎵", "MP3 Audio",
            "High quality audio extraction", "audio")
        self.card_audio.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self._refresh_mode()
    def _mode_card(self, parent, icon, title, desc, value):
        card = ctk.CTkFrame(parent, fg_color=SURFACE_2, corner_radius=14,
                            border_width=1, border_color=BORDER, height=92)
        card.pack_propagate(False)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)
        ic = ctk.CTkLabel(inner, text=icon, font=f(26))
        ic.pack(side="left", padx=(0, 14))
        txt = ctk.CTkFrame(inner, fg_color="transparent")
        txt.pack(side="left", fill="both", expand=True)
        t = ctk.CTkLabel(txt, text=title, font=f(14, "bold"), text_color=TEXT)
        t.pack(anchor="w")
        d = ctk.CTkLabel(txt, text=desc, font=f(12), text_color=TEXT_DIM)
        d.pack(anchor="w")
        dot = ctk.CTkFrame(inner, width=18, height=18, corner_radius=999,
                           fg_color=SURFACE_3, border_width=1, border_color=BORDER)
        dot.pack(side="right")
        dot.pack_propagate(False)
        card._dot = dot
        card._title = t
        card._desc = d
        card._value = value
        for w in (card, inner, ic, txt, t, d):
            w.bind("<Button-1>", lambda e, v=value: self._set_mode(v))
            w.configure(cursor="hand2")
        return card
    def _set_mode(self, value):
        self.mode.set(value)
        self._refresh_mode()

        if self.url_var.get().strip():
            self.load_preview(self.url_var.get().strip())
    def _refresh_mode(self):
        for card in (self.card_video, self.card_audio):
            selected = card._value == self.mode.get()
            card.configure(
                border_color=ACCENT if selected else BORDER,
                fg_color="#16243F" if selected else SURFACE_2,
                border_width=2 if selected else 1,
            )
            card._dot.configure(
                fg_color=ACCENT if selected else SURFACE_3,
                border_color=ACCENT_GLOW if selected else BORDER,
            )
    # ---- Folder ----
    def _section_folder(self, parent):
        ctk.CTkLabel(parent, text="Download Location",
                     font=f(13, "bold"), text_color=TEXT_DIM
                     ).pack(anchor="w", pady=(20, 8))
        box = ctk.CTkFrame(parent, fg_color=SURFACE_2, corner_radius=14,
                           border_width=1, border_color=BORDER, height=64)
        box.pack(fill="x")
        box.pack_propagate(False)
        ic_wrap = ctk.CTkFrame(box, width=40, height=40, corner_radius=10,
                               fg_color=SURFACE_3)
        ic_wrap.pack(side="left", padx=(14, 12), pady=12)
        ic_wrap.pack_propagate(False)
        ctk.CTkLabel(ic_wrap, text="📁", font=f(18)).pack(expand=True)
        txt = ctk.CTkFrame(box, fg_color="transparent")
        txt.pack(side="left", fill="both", expand=True, pady=10)
        ctk.CTkLabel(txt, text="Saved to", font=f(11),
                     text_color=TEXT_MUTED).pack(anchor="w")
        self.folder_lbl = ctk.CTkLabel(txt, textvariable=self.folder,
                                       font=f(13, "bold"), text_color=TEXT)
        self.folder_lbl.pack(anchor="w")
        ctk.CTkButton(box, text="Browse", width=100, height=38,
                      corner_radius=10, font=f(12, "bold"),
                      fg_color=SURFACE_3, hover_color=BORDER, text_color=TEXT,
                      command=self._browse).pack(side="right", padx=14)
    def _browse(self):
        path = filedialog.askdirectory(initialdir=self.folder.get())
        if path:
            self.folder.set(path)
    # ---- Download button ----
    def _section_download_btn(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", pady=(24, 4))
        self.dl_btn = ctk.CTkButton(
            wrap, text="⬇   DOWNLOAD", height=58, corner_radius=16,
            font=f(15, "bold"), fg_color=ACCENT, hover_color=ACCENT_HOV,
            text_color="#FFFFFF", command=self._start_demo,
        )
        self.dl_btn.pack(fill="x")
    # ---- Progress ----
    def _section_progress(self, parent):
        self.prog_card = ctk.CTkFrame(parent, fg_color=SURFACE_2,
                                      corner_radius=16, border_width=1,
                                      border_color=BORDER)
        self.prog_card.pack(fill="x", pady=(20, 0))
        top = ctk.CTkFrame(self.prog_card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(18, 6))
        self.state_lbl = ctk.CTkLabel(top, text="Idle", font=f(14, "bold"),
                                      text_color=TEXT)
        self.state_lbl.pack(side="left")
        self.pct_lbl = ctk.CTkLabel(top, text="0%", font=f(14, "bold"),
                                    text_color=ACCENT_GLOW)
        self.pct_lbl.pack(side="right")
        self.bar = ctk.CTkProgressBar(
            self.prog_card, height=10, corner_radius=8,
            progress_color=ACCENT, fg_color=SURFACE_3,
        )
        self.bar.set(0)
        self.bar.pack(fill="x", padx=20, pady=(2, 10))
        meta = ctk.CTkFrame(self.prog_card, fg_color="transparent")
        meta.pack(fill="x", padx=20, pady=(0, 18))
        self.speed_lbl = ctk.CTkLabel(meta, text="Speed —",
                                      font=f(12), text_color=TEXT_DIM)
        self.speed_lbl.pack(side="left")
        self.eta_lbl = ctk.CTkLabel(meta, text="ETA —",
                                    font=f(12), text_color=TEXT_DIM)
        self.eta_lbl.pack(side="right")
        # Success layer (hidden by default)
        self.success_card = ctk.CTkFrame(parent, fg_color="#0E2A22",
                                         corner_radius=16, border_width=1,
                                         border_color="#1F5A45")
        # Not packed yet
        s_inner = ctk.CTkFrame(self.success_card, fg_color="transparent")
        s_inner.pack(fill="x", padx=20, pady=18)
        check = ctk.CTkFrame(s_inner, width=44, height=44, corner_radius=22,
                             fg_color=SUCCESS)
        check.pack(side="left", padx=(0, 14))
        check.pack_propagate(False)
        ctk.CTkLabel(check, text="✓", font=f(22, "bold"),
                     text_color="#FFFFFF").pack(expand=True)
        s_txt = ctk.CTkFrame(s_inner, fg_color="transparent")
        s_txt.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(s_txt, text="Download Completed Successfully",
                     font=f(14, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(s_txt, text="Your file is ready in the destination folder.",
                     font=f(12), text_color=TEXT_DIM).pack(anchor="w")
        actions = ctk.CTkFrame(s_inner, fg_color="transparent")
        actions.pack(side="right")
        ctk.CTkButton(actions, text="Open Folder", height=36, width=120,
                      corner_radius=10, font=f(12, "bold"),
                      fg_color=SUCCESS, hover_color=SUCCESS_HOV,
                      command=self._open_folder).pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="Download Another", height=36, width=150,
                      corner_radius=10, font=f(12, "bold"),
                      fg_color=SURFACE_3, hover_color=BORDER, text_color=TEXT,
                      command=self._reset).pack(side="left")
    # =================== FOOTER ===================
    def _build_footer(self):
        bar = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=34,
                           border_width=0)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        ctk.CTkLabel(bar, text="●  Connected", font=f(11, "bold"),
                     text_color=SUCCESS).pack(side="left", padx=14)
        ctk.CTkLabel(bar, text="v1.0  ·  Ayan Downloader",
                     font=f(11), text_color=TEXT_MUTED).pack(side="right", padx=14)
    # =================== DEMO PROGRESS ===================
    def _open_folder(self):
        try:
            os.startfile(self.folder.get())
        except Exception:
            pass
    def _reset(self):
        self.success_card.pack_forget()
        self.prog_card.pack(fill="x", pady=(20, 0))
        self.bar.set(0)
        self.pct_lbl.configure(text="0%")
        self.state_lbl.configure(text="Idle")
        self.speed_lbl.configure(text="Speed —")
        self.eta_lbl.configure(text="ETA —")
        self.dl_btn.configure(state="normal")
    def _start_demo(self):
        self.dl_btn.configure(state="disabled")
        threading.Thread(target=self._run_demo, daemon=True).start()
    def _run_demo(self):
        stages = [
            ("Fetching Information…", 0, 8, 0.04),
            ("Downloading Video", 8, 78, 0.025),
            ("Processing Audio…", 78, 90, 0.05),
            ("Merging Files…", 90, 100, 0.06),
        ]
        for label, a, b, delay in stages:
            self.after(0, self.state_lbl.configure, {"text": label})
            for p in range(a, b + 1):
                self.after(0, self.bar.set, p / 100)
                self.after(0, self.pct_lbl.configure, {"text": f"{p}%"})
                self.after(0, self.speed_lbl.configure,
                           {"text": f"Speed  {8 + (p % 9)}.{p % 10} MB/s"})
                remaining = max(0, (100 - p) // 3)
                self.after(0, self.eta_lbl.configure,
                           {"text": f"ETA  00:{remaining:02d}"})
                time.sleep(delay)
        self.after(0, self._show_success)

    def _show_success(self):
        self.state_lbl.configure(text="Completed")
        self.prog_card.pack_forget()
        self.success_card.pack(fill="x", pady=(20, 0))
        self.dl_btn.configure(state="normal")

    def select_quality(self, quality):
        self.selected_quality = quality

        for chip, value in self.quality_chips:
            if value == quality:
                chip.configure(fg_color=ACCENT, border_color=ACCENT)
            else:
                chip.configure(fg_color=SURFACE_3, border_color=BORDER)