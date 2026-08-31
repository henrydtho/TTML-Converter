#!/usr/bin/env python3
"""Convert IMSC TTML text colors from SDR to HDR values."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET

from tkinterdnd2 import DND_FILES, TkinterDnD

from ttml_conversion import convert_to_hdr, suggested_destination

class ConverterApp:
    def __init__(self, root: TkinterDnD.Tk) -> None:
        self.root = root
        self.source_paths: list[Path] = []
        self.destination_directory = tk.StringVar()
        self.status = tk.StringVar(value="Drop up to 100 SDR TTML files here or select them.")

        root.title("TTML HDR Converter V3")
        root.minsize(620, 340)
        root.columnconfigure(0, weight=1)

        frame = ttk.Frame(root, padding=24)
        frame.grid(sticky="nsew")
        frame.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        ttk.Label(frame, text="TTML HDR Converter V3", font=("Helvetica", 20, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            frame,
            text="Applies HDR color and black outline settings to text styles.",
        ).grid(row=1, column=0, sticky="w", pady=(4, 18))

        self.drop_zone = ttk.Label(
            frame,
            text="Drop up to 100 SDR .ttml files here\n(or click Select Files)",
            anchor="center",
            relief="solid",
            padding=28,
        )
        self.drop_zone.grid(row=2, column=0, sticky="ew")
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind("<<Drop>>", self.on_drop)

        ttk.Button(frame, text="Select Files", command=self.select_sources).grid(
            row=3, column=0, sticky="w", pady=(12, 18)
        )

        output = ttk.Frame(frame)
        output.grid(row=4, column=0, sticky="ew")
        output.columnconfigure(0, weight=1)
        ttk.Label(output, text="HDR output folder").grid(row=0, column=0, sticky="w")
        ttk.Entry(output, textvariable=self.destination_directory).grid(
            row=1, column=0, sticky="ew", pady=(4, 0)
        )
        ttk.Button(output, text="Choose Folder", command=self.choose_destination).grid(
            row=1, column=1, padx=(8, 0), pady=(4, 0)
        )

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, sticky="ew", pady=(20, 0))
        ttk.Button(buttons, text="Convert to HDR", command=self.convert).pack(side="left")
        ttk.Label(frame, textvariable=self.status, wraplength=560).grid(
            row=6, column=0, sticky="w", pady=(16, 0)
        )

    def on_drop(self, event: tk.Event) -> None:
        paths = self.root.tk.splitlist(event.data)
        self.set_sources([Path(path) for path in paths])

    def select_sources(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Select SDR TTML files",
            filetypes=[("TTML files", "*.ttml"), ("All files", "*.*")],
        )
        if selected:
            self.set_sources([Path(path) for path in selected])

    def set_sources(self, sources: list[Path]) -> None:
        valid_sources = [source for source in sources if source.suffix.lower() == ".ttml"]
        if len(valid_sources) != len(sources) or not valid_sources:
            messagebox.showerror("Invalid file", "Select only files with a .ttml extension.")
            return
        if len(valid_sources) > 100:
            messagebox.showerror("Too many files", "Select no more than 100 TTML files at a time.")
            return
        self.source_paths = valid_sources
        if not self.destination_directory.get():
            self.destination_directory.set(str(valid_sources[0].parent))
        self.status.set(f"Ready: {len(valid_sources)} TTML file(s) selected.")

    def choose_destination(self) -> None:
        selected = filedialog.askdirectory(
            title="Choose HDR output folder",
            initialdir=self.destination_directory.get() or str(Path.home()),
        )
        if selected:
            self.destination_directory.set(selected)

    def convert(self) -> None:
        if not self.source_paths:
            messagebox.showerror("Source required", "Drop or select TTML files first.")
            return
        if not self.destination_directory.get():
            messagebox.showerror("Output required", "Choose where to save the HDR TTML files.")
            return

        destination_directory = Path(self.destination_directory.get())
        converted_files = 0
        updated_styles = 0
        failures: list[str] = []
        for source in self.source_paths:
            try:
                updated_styles += convert_to_hdr(source, destination_directory / suggested_destination(source).name)
                converted_files += 1
            except (ET.ParseError, OSError, ValueError) as error:
                failures.append(f"{source.name}: {error}")

        if failures:
            messagebox.showerror("Some conversions failed", "\n".join(failures))
        if not converted_files:
            self.status.set("Conversion failed.")
            return

        self.status.set(f"Converted {converted_files} file(s) and {updated_styles} text style(s).")
        messagebox.showinfo("Conversion complete", f"Saved HDR TTML files to:\n{destination_directory}")


if __name__ == "__main__":
    application_root = TkinterDnD.Tk()
    ConverterApp(application_root)
    application_root.mainloop()