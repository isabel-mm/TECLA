"""
Main corpus-building pipeline for the TECLA corpus module.

This module orchestrates:
- PDF discovery,
- metadata inference,
- PDF-to-text conversion,
- optional cleaning (structural, linguistic, bibliography removal, etc.),
- writing raw and cleaned TXT files,
- metadata CSV generation,
- optional descriptive statistics.

The design prioritises transparency, reproducibility, and simplicity for users
with little or no programming background.
"""

import os
import csv

from .utils import list_pdfs, ensure_folder
from .metadata import infer_metadata
from .pdf_to_txt import pdf_to_text
from .cleaning import clean_text
from .statistics import corpus_statistics


# ---------------------------------------------------------------------------
# HELPER: WRITE TXT FILES
# ---------------------------------------------------------------------------

def _write_txt(path, text):
    """
    Write text to a UTF-8 TXT file.

    Parameters:
        path (str)
        text (str)
    """
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

    Parameters:
        input_folder (str): Directory containing PDFs.
        out_folder (str): Folder where TXT files will be saved.
                          Structure:
                            out_folder/raw/
                            out_folder/clean/ (if clean=True)
        metadata_file (str): Path to metadata CSV.
        clean (bool): Whether to apply text cleaning.
        clean_params (dict or None): Parameters for cleaning.
        compute_stats (bool): Whether to compute corpus-level statistics.
        stats_output (str): Path to save statistics CSV.

    Returns:
        dict: {
            "metadata": list of metadata dicts,
            "statistics": corpus_stats or None
        }
    """

    # defaults to avoid None checks
    if clean_params is None:
        clean_params = {}

    # Ensure output directories -------------------------------------------------
    raw_dir = ensure_folder(os.path.join(out_folder, "raw"))
    clean_dir = ensure_folder(os.path.join(out_folder, "clean")) if clean else None

    # Find PDFs -----------------------------------------------------------------
    pdf_paths = list_pdfs(input_folder)
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found in: {input_folder}")

    metadata_rows = []

    # Process each PDF ----------------------------------------------------------
    for pdf_path in pdf_paths:
        filename = os.path.basename(pdf_path)
        fname_no_ext = os.path.splitext(filename)[0]

        # 1. Metadata inference
        meta = infer_metadata(filename)
        meta["pdf_path"] = pdf_path

        # 2. PDF → text
        raw_text = pdf_to_text(pdf_path)

        # 3. Save raw text
        raw_txt_path = os.path.join(raw_dir, f"{fname_no_ext}.txt")
        _write_txt(raw_txt_path, raw_text)
        meta["raw_txt_path"] = raw_txt_path

        # 4. Clean text if requested
        if clean:
            cleaned = clean_text(raw_text, **clean_params)
            clean_txt_path = os.path.join(clean_dir, f"{fname_no_ext}.txt")
            _write_txt(clean_txt_path, cleaned)
            meta["clean_txt_path"] = clean_txt_path
        else:
            meta["clean_txt_path"] = None

        metadata_rows.append(meta)

    # ---------------------------------------------------------------------------
    # WRITE METADATA CSV
    # ---------------------------------------------------------------------------

    metadata_fields = [
        "file", "author", "title", "year", "text_type",
        "pdf_path", "raw_txt_path", "clean_txt_path"
    ]

    # Normalise field names
    for m in metadata_rows:
        m["file"] = os.path.basename(m["pdf_path"])

    with open(metadata_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(metadata_fields)

        for row in metadata_rows:
            writer.writerow([row.get(f, "") for f in metadata_fields])

    # ---------------------------------------------------------------------------
    # OPTIONAL STATISTICS
    # ---------------------------------------------------------------------------

    stats = None
    if compute_stats:
        folder_for_stats = clean_dir if clean else raw_dir

        from .statistics import corpus_statistics, compute_global_statistics

        # Document-level statistics
        stats_list = corpus_statistics(folder_for_stats, output_csv=None)

        # Global corpus statistics
        global_stats = compute_global_statistics(stats_list)
        stats_list.append(global_stats)

        # Save final CSV with all statistics
        with open(stats_output, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(stats_list[0].keys()))
            writer.writeheader()
            for row in stats_list:
                writer.writerow(row)

        stats = stats_list

    return {
        "metadata": metadata_rows,
        "statistics": stats
    }
