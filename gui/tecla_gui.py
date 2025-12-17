import customtkinter as ctk
from tkinter import filedialog
import os
from pathlib import Path

from tecla.corpus.builder import build_corpus
from tecla.extractor.hybrid_extractor import HybridTermExtractor

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

        ctk.CTkLabel(
            self.options_frame,
            text="Corpus folder"
        ).pack(anchor="w", padx=15)

        corpus_entry = ctk.CTkEntry(
            self.options_frame,
            textvariable=self.corpus_path_var
        )
        corpus_entry.pack(fill="x", padx=15, pady=(0, 5))

        browse_button = ctk.CTkButton(
            self.options_frame,
            text="Browse…",
            command=self._browse_corpus
        )
        browse_button.pack(fill="x", padx=15, pady=(0, 20))

        # ---------------- Language selector ----------------

        self.language_var = ctk.StringVar(value="en")

        ctk.CTkLabel(self.options_frame, text="Language").pack(anchor="w", padx=15)
        ctk.CTkOptionMenu(
            self.options_frame,
            values=["en", "es"],
            variable=self.language_var
        ).pack(fill="x", padx=15, pady=(0, 15))

        # ---------------- Term length ----------------

        self.multiword_var = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(
            self.options_frame,
            text="Multi-word terms only",
            variable=self.multiword_var
        ).pack(anchor="w", padx=15, pady=5)

        # ---------------- Weights ----------------

        ctk.CTkLabel(
            self.options_frame,
            text="Weights"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.tfidf_weight = ctk.DoubleVar(value=0.8)
        self.cvalue_weight = ctk.DoubleVar(value=0.2)

        ctk.CTkLabel(self.options_frame, text="TF-IDF").pack(anchor="w", padx=15)
        ctk.CTkSlider(
            self.options_frame,
            from_=0.0,
            to=1.0,
            variable=self.tfidf_weight
        ).pack(fill="x", padx=15)

        ctk.CTkLabel(
            self.options_frame,
            text="C-value"
        ).pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkSlider(
            self.options_frame,
            from_=0.0,
            to=1.0,
            variable=self.cvalue_weight
        ).pack(fill="x", padx=15)

        # ---------------- Run button ----------------

        self.run_button = ctk.CTkButton(
            self.options_frame,
            text="Run extraction",
            command=self.run_extraction
        )
        self.run_button.pack(fill="x", padx=15, pady=30)

    # -----------------------------------------------------------------
    # Results panel
    # -----------------------------------------------------------------

    def _build_results(self):

        title = ctk.CTkLabel(
            self.results_frame,
            text="Results",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(anchor="w", padx=15, pady=(10, 5))

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
        """
        Run TECLA pipeline:
        1) build corpus
        2) extract terms
        3) show results
        """

        self.output_box.delete("1.0", "end")

        corpus_path = self.corpus_path_var.get()

        if not corpus_path or not os.path.isdir(corpus_path):
            self.output_box.insert("end", "⚠️ Please select a valid corpus folder.\n")
            return

        language = self.language_var.get()

        # ---------------- Build corpus ----------------

        self.output_box.insert("end", "📚 Building corpus...\n")
        self.update_idletasks()

        try:
            documents = build_corpus(
                input_folder=corpus_path,
                out_folder=os.path.join(corpus_path, "_tecla_txt"),
                metadata_file=os.path.join(corpus_path, "metadata.csv"),
                clean=True,
                clean_params={
                    "structure": True,
                    "remove_stopwords_flag": False,
                    "lemmatize_flag": True,
                    "remove_bibliography_flag": True,
                    "language": language,
                },
                compute_stats=False,
            )
        except Exception as e:
            self.output_box.insert("end", f"\n❌ Error while building corpus:\n{e}\n")
            return

        self.output_box.insert("end", f"✅ Corpus built ({len(documents)} documents)\n\n")
        self.update_idletasks()

        # ---------------- Extractor ----------------

        weights = {
            "tfidf": round(self.tfidf_weight.get(), 2),
            "cvalue": round(self.cvalue_weight.get(), 2),
        }

        if self.multiword_var.get():
            term_length = (2, None)
        else:
            term_length = None

        extractor = HybridTermExtractor(
            language=language,
            weights=weights,
        )

        self.output_box.insert("end", "🔍 Extracting terms...\n")
        self.update_idletasks()

        try:
            results = extractor.extract(
                documents=documents,
                percentile=90,
                term_length=term_length,
            )
        except Exception as e:
            self.output_box.insert("end", f"\n❌ Error during extraction:\n{e}\n")
            return

        # ---------------- Show results ----------------

        self.output_box.insert("end", f"\n🏁 Extraction finished: {len(results)} terms\n\n")

        for i, term in enumerate(results[:50], start=1):
            self.output_box.insert(
                "end",
                f"{i:>3}. {term['term']}  ({term['terminologicity']:.3f})\n"
            )


# ---------------------------------------------------------------------
# Run app
# ---------------------------------------------------------------------

if __name__ == "__main__":
    app = TeclaApp()
    app.mainloop()
