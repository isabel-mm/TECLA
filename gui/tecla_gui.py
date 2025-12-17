import customtkinter as ctk
from tkinter import filedialog
import os
from pathlib import Path
import time

# ---------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------

ctk.set_appearance_mode("light")   # también puedes probar "dark"
ctk.set_default_color_theme("blue")


class TeclaApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("TECLA – Terminology Extraction")
        self.geometry("1000x650")
        self.minsize(900, 600)

        # Shared variables
        self.corpus_path_var = ctk.StringVar(value="")
        self.language_var = ctk.StringVar(value="en")
        self.multiword_var = ctk.BooleanVar(value=True)
        self.tfidf_weight = ctk.DoubleVar(value=0.8)
        self.cvalue_weight = ctk.DoubleVar(value=0.2)

        # ---------------- Main layout ----------------
        self._build_layout()

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------

    def _build_layout(self):

        # Left panel (options)
        self.options_frame = ctk.CTkFrame(self, width=300)
        self.options_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Right panel (results)
        self.results_frame = ctk.CTkFrame(self)
        self.results_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self._build_options()
        self._build_results()

    # -----------------------------------------------------------------
    # Options panel
    # -----------------------------------------------------------------

    def _build_options(self):

        title = ctk.CTkLabel(
            self.options_frame,
            text="Extraction options",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(10, 20))

        # ---------------- Corpus selector ----------------

        ctk.CTkLabel(self.options_frame, text="Corpus folder").pack(anchor="w", padx=15)

        ctk.CTkEntry(
            self.options_frame,
            textvariable=self.corpus_path_var
        ).pack(fill="x", padx=15, pady=(0, 5))

        ctk.CTkButton(
            self.options_frame,
            text="Browse…",
            command=self._browse_corpus
        ).pack(fill="x", padx=15, pady=(0, 20))

        # ---------------- Language ----------------

        ctk.CTkLabel(self.options_frame, text="Language").pack(anchor="w", padx=15)
        ctk.CTkOptionMenu(
            self.options_frame,
            values=["en", "es"],
            variable=self.language_var
        ).pack(fill="x", padx=15, pady=(0, 15))

        # ---------------- Term length ----------------

        ctk.CTkCheckBox(
            self.options_frame,
            text="Multi-word terms only",
            variable=self.multiword_var
        ).pack(anchor="w", padx=15, pady=5)

        # ---------------- Weights ----------------

        ctk.CTkLabel(self.options_frame, text="Weights").pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(self.options_frame, text="TF-IDF").pack(anchor="w", padx=15)
        ctk.CTkSlider(
            self.options_frame,
            from_=0.0,
            to=1.0,
            variable=self.tfidf_weight
        ).pack(fill="x", padx=15)

        ctk.CTkLabel(self.options_frame, text="C-value").pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkSlider(
            self.options_frame,
            from_=0.0,
            to=1.0,
            variable=self.cvalue_weight
        ).pack(fill="x", padx=15)

        # ---------------- Run ----------------

        ctk.CTkButton(
            self.options_frame,
            text="Run extraction",
            command=self.run_extraction
        ).pack(fill="x", padx=15, pady=30)

    # -----------------------------------------------------------------
    # Results panel
    # -----------------------------------------------------------------

    def _build_results(self):

        ctk.CTkLabel(
            self.results_frame,
            text="Results",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.output_box = ctk.CTkTextbox(self.results_frame)
        self.output_box.pack(fill="both", expand=True, padx=15, pady=10)

    # -----------------------------------------------------------------
    # Actions
    # -----------------------------------------------------------------

    def _browse_corpus(self):
        folder = filedialog.askdirectory(title="Select corpus folder")
        if folder:
            self.corpus_path_var.set(folder)

    def run_extraction(self):
        """MOCK extraction (MVP)"""

        self.output_box.delete("1.0", "end")

        if not self.corpus_path_var.get():
            self.output_box.insert("end", "⚠️ Please select a corpus folder.\n")
            return

        self.output_box.insert("end", "📚 Building corpus...\n")
        self.update_idletasks()
        time.sleep(0.5)

        self.output_box.insert("end", "🔍 Extracting candidate terms...\n")
        self.update_idletasks()
        time.sleep(0.5)

        self.output_box.insert("end", "📊 Computing termhood...\n\n")
        self.update_idletasks()
        time.sleep(0.5)

        # -------- MOCK RESULTS --------

        mock_terms = [
            ("corpus linguistics", 0.92),
            ("annotation scheme", 0.87),
            ("term extraction", 0.84),
            ("domain specificity", 0.81),
            ("linguistic filter", 0.78),
            ("statistical weighting", 0.75),
        ]

        self.output_box.insert(
            "end",
            f"🏁 Extraction finished: {len(mock_terms)} terms\n\n"
        )

        for i, (term, score) in enumerate(mock_terms, start=1):
            self.output_box.insert(
                "end",
                f"{i:>3}. {term}  ({score:.3f})\n"
            )


# ---------------------------------------------------------------------
# Run app
# ---------------------------------------------------------------------

if __name__ == "__main__":
    app = TeclaApp()
    app.mainloop()
