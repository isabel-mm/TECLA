"""
Main corpus-building pipeline for the TECLA corpus module.

This module performs the sequential construction of a corpus from PDFs:

1. Discover PDF files.
2. Infer metadata from filenames.
3. Convert PDF → raw text.
4. Optional cleaning (structure, stopwords, lemmatisation, bibliography removal).
5. Write raw and cleaned TXT files.
6. Generate metadata.csv.
7. Optional descriptive statistics (document-level + global-level).

The goal is transparency, reproducibility and simplicity.
"""

import os
import csv

from .utils import list_pdfs, ensure_folder
from .metadata import infer_metadata
from .pdf_to_txt import pdf_to_text
from .cleaning import clean_text
from .statistics import corpus_statistics, compute_global_statistics


# ---------------------------------------------------------------------------
# INTERNAL: SHARED STATS WRITER
# ---------------------------------------------------------------------------

def _write_stats_csv(doc_stats, stats_output):
    """Write per-document and global statistics to CSV."""
    global_stats = compute_global_statistics(doc_stats)
    doc_stats.append(global_stats)

    header = [
        "filename", "token_count", "type_count", "ttr",
        "hapax_ratio", "stopword_ratio", "lexical_density",
        "sentence_count", "avg_sentence_length"
    ]
    with open(stats_output, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for row in doc_stats:
            writer.writerow({h: row.get(h, "") for h in header})

    return doc_stats


# ---------------------------------------------------------------------------
# ALTERNATIVE ENTRY POINT: BUILD CORPUS FROM TXT
# ---------------------------------------------------------------------------

def build_corpus_from_txt(
    input_folder,
    out_folder="corpus_txt",
    metadata_file="metadata.csv",
    clean=False,
    clean_params=None,
    compute_stats=False,
    stats_output="corpus_stats.csv",
):
    """
    Build a corpus starting from plain-text (.txt) files instead of PDFs.

    Useful when texts have already been extracted or obtained from other
    sources. Skips the PDF-conversion step and proceeds directly to
    optional cleaning, metadata inference and statistics.

    Parameters
    ----------
    input_folder : str
        Folder containing .txt files.
    out_folder : str
        Base output folder. Raw texts are symlinked/copied to out_folder/raw/
        and cleaned texts written to out_folder/clean/.
    metadata_file : str
        Path for the output metadata CSV.
    clean : bool
        Whether to apply cleaning operations.
    clean_params : dict or None
        Cleaning options forwarded to clean_text().
    compute_stats : bool
        Whether to compute and export corpus statistics.
    stats_output : str
        Path for the output statistics CSV.

    Returns
    -------
    dict
        Same structure as build_corpus():
        {"metadata": list, "statistics": list or None}
    """

    if clean_params is None:
        clean_params = {}

    # ------------------------------------------------------------------
    # Ensure input folder
    # ------------------------------------------------------------------
    if not os.path.isdir(input_folder):
        os.makedirs(input_folder, exist_ok=True)
        print(
            f"📂 The folder '{input_folder}' did not exist and has been created.\n"
            f"➡️  Add .txt files and run build_corpus_from_txt() again."
        )
        return {
            "metadata": [],
            "statistics": None,
            "message": f"Input folder '{input_folder}' created — no TXT files found yet.",
        }

    # ------------------------------------------------------------------
    # Discover TXT files (recursively, skipping TECLA output folder)
    # ------------------------------------------------------------------
    txt_files = []
    for dirpath, dirnames, filenames in os.walk(input_folder):
        dirnames[:] = [d for d in dirnames if d != "_tecla_txt"]
        for f in filenames:
            if f.lower().endswith(".txt"):
                txt_files.append(os.path.join(dirpath, f))
    txt_files.sort()

    if not txt_files:
        print(
            f"⚠️ No .txt files found in '{input_folder}'.\n"
            f"➡️  Add text files and re-run build_corpus_from_txt()."
        )
        return {
            "metadata": [],
            "statistics": None,
            "message": f"No TXT files found in '{input_folder}'.",
        }

    # ------------------------------------------------------------------
    # Ensure output directories
    # ------------------------------------------------------------------
    raw_dir = ensure_folder(os.path.join(out_folder, "raw"))
    clean_dir = ensure_folder(os.path.join(out_folder, "clean")) if clean else None

    metadata_rows = []

    for txt_path in txt_files:
        filename = os.path.basename(txt_path)

        meta = infer_metadata(filename)
        meta["pdf_path"] = ""

        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()

        # Copy raw text to output raw folder
        raw_out = os.path.join(raw_dir, filename)
        _write_txt(raw_out, raw_text)
        meta["raw_txt_path"] = raw_out

        if clean:
            cleaned = clean_text(raw_text, **clean_params)
            clean_out = os.path.join(clean_dir, filename)
            _write_txt(clean_out, cleaned)
            meta["clean_txt_path"] = clean_out
        else:
            meta["clean_txt_path"] = None

        meta["file"] = filename
        metadata_rows.append(meta)

    # ------------------------------------------------------------------
    # Write metadata CSV
    # ------------------------------------------------------------------
    metadata_fields = [
        "file", "author", "title", "year", "source", "text_type",
        "pdf_path", "raw_txt_path", "clean_txt_path"
    ]
    with open(metadata_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(metadata_fields)
        for row in metadata_rows:
            writer.writerow([row.get(f, "") for f in metadata_fields])

    # ------------------------------------------------------------------
    # Optional statistics
    # ------------------------------------------------------------------
    stats = None
    if compute_stats:
        folder_for_stats = clean_dir if clean else raw_dir
        doc_stats = corpus_statistics(
            input_folder=folder_for_stats,
            language=clean_params.get("language", "en"),
            stoplist=clean_params.get("stoplist"),
            extra_stoplist=clean_params.get("extra_stoplist"),
            output_csv=None,
        )
        stats = _write_stats_csv(doc_stats, stats_output)

    return {"metadata": metadata_rows, "statistics": stats}


# ---------------------------------------------------------------------------
# INTERNAL: WRITE TXT
# ---------------------------------------------------------------------------

def _write_txt(path, text):
    """Write a UTF-8 text file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ---------------------------------------------------------------------------
# MAIN FUNCTION: BUILD CORPUS
# ---------------------------------------------------------------------------

def build_corpus(
    input_folder,
    out_folder="corpus_txt",
    metadata_file="metadata.csv",
    clean=False,
    clean_params=None,
    compute_stats=False,
    stats_output="corpus_stats.csv",
):
    """
    Build a corpus from a folder of PDF files.

    If input_folder does not exist, TECLA creates it automatically
    and stops the pipeline with a user-friendly message.
    If the folder exists but is empty, TECLA informs the user as well.

    Returns
    -------
    dict with keys:
        "metadata": list of metadata dicts
        "statistics": list of stats rows (if compute_stats=True)
    """

    # ----------------------------------------------------------------------
    # 0. Ensure input_folder exists
    # ----------------------------------------------------------------------
    if not os.path.isdir(input_folder):
        os.makedirs(input_folder, exist_ok=True)
        print(
            f"📂 The folder '{input_folder}' did not exist and has been created.\n"
            f"➡️  Add PDF files to this folder and run build_corpus() again."
        )
        return {
            "metadata": [],
            "statistics": None,
            "message": f"Input folder '{input_folder}' created — no PDFs found yet."
        }

    # ----------------------------------------------------------------------
    # Default cleaning params
    # ----------------------------------------------------------------------
    if clean_params is None:
        clean_params = {}

    # ----------------------------------------------------------------------
    # Ensure output directories
    # ----------------------------------------------------------------------
    raw_dir = ensure_folder(os.path.join(out_folder, "raw"))
    clean_dir = ensure_folder(os.path.join(out_folder, "clean")) if clean else None

    # ----------------------------------------------------------------------
    # Locate PDFs
    # ----------------------------------------------------------------------
    pdf_paths = list_pdfs(input_folder)

    if not pdf_paths:
        print(
            f"⚠️ No PDF files found in '{input_folder}'.\n"
            f"➡️  Add PDFs to the folder and re-run build_corpus()."
        )
        return {
            "metadata": [],
            "statistics": None,
            "message": f"No PDFs found in '{input_folder}'."
        }

    metadata_rows = []

    # ----------------------------------------------------------------------
    # PROCESS EACH PDF
    # ----------------------------------------------------------------------
    for pdf_path in pdf_paths:
        filename = os.path.basename(pdf_path)
        fname_no_ext = os.path.splitext(filename)[0]

        # Metadata inference
        meta = infer_metadata(filename)
        meta["pdf_path"] = pdf_path

        # PDF → raw text
        raw_text = pdf_to_text(pdf_path)

        # Save raw text
        raw_txt_path = os.path.join(raw_dir, f"{fname_no_ext}.txt")
        _write_txt(raw_txt_path, raw_text)
        meta["raw_txt_path"] = raw_txt_path

        # Cleaned version
        if clean:
            cleaned = clean_text(raw_text, **clean_params)
            clean_txt_path = os.path.join(clean_dir, f"{fname_no_ext}.txt")
            _write_txt(clean_txt_path, cleaned)
            meta["clean_txt_path"] = clean_txt_path
        else:
            meta["clean_txt_path"] = None

        # Normalize filename field
        meta["file"] = filename

        metadata_rows.append(meta)

    # ----------------------------------------------------------------------
    # WRITE METADATA CSV
    # ----------------------------------------------------------------------
    metadata_fields = [
        "file", "author", "title", "year", "source", "text_type",
        "pdf_path", "raw_txt_path", "clean_txt_path"
    ]

    with open(metadata_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(metadata_fields)

        for row in metadata_rows:
            writer.writerow([row.get(f, "") for f in metadata_fields])

    # ----------------------------------------------------------------------
    # OPTIONAL: STATISTICS
    # ----------------------------------------------------------------------
    stats = None

    if compute_stats:

        # If cleaning enabled → statistics computed from cleaned texts
        folder_for_stats = clean_dir if clean else raw_dir

        # Document-level statistics
        doc_stats = corpus_statistics(
            input_folder=folder_for_stats,
            language=clean_params.get("language", "en"),
            stoplist=clean_params.get("stoplist"),
            extra_stoplist=clean_params.get("extra_stoplist"),
            output_csv=None
        )

        # Corpus-level global statistics
        global_stats = compute_global_statistics(doc_stats)

        # Append global row
        doc_stats.append(global_stats)

        # Write CSV
        with open(stats_output, "w", newline="", encoding="utf-8") as csvfile:
            header = [
                "filename", "token_count", "type_count", "ttr",
                "hapax_ratio", "stopword_ratio", "lexical_density",
                "sentence_count", "avg_sentence_length"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()

            for row in doc_stats:
                writer.writerow({h: row.get(h, "") for h in header})

        stats = doc_stats

    # ----------------------------------------------------------------------
    # Return structured output
    # ----------------------------------------------------------------------
    return {
        "metadata": metadata_rows,
        "statistics": stats
    }
