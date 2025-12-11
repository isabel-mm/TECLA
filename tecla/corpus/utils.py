"""
Utility functions used internally by the TECLA corpus module.

These helpers manage:
- folder creation,
- PDF file discovery,
- stoplist loading,
- safe file reading and writing.

All functions here are intended for internal use.
"""

import os
import csv


def list_pdfs(folder):
    """
    Return a list of full paths to all PDF files found in a folder.

    Parameters:
        folder (str): Path to the directory containing PDF files.

    Returns:
        list[str]: Full paths to all PDF files.
    """
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Input folder does not exist: {folder}")

    pdfs = []
    for f in os.listdir(folder):
        if f.lower().endswith(".pdf"):
            pdfs.append(os.path.join(folder, f))

    return sorted(pdfs)



def ensure_folder(path):
    """
    Create a folder if it does not already exist.

    Parameters:
        path (str): Directory path to create.

    Returns:
        str: The validated directory path.
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path


def load_stoplist(stoplist):
    """
    Load a stoplist from a file path or accept a user-provided list.

    Parameters:
        stoplist (str or list or None):
            - If None: return an empty set (caller decides default behaviour).
            - If str: interpret it as a file path (one token per line).
            - If list: convert it into a set.

    Returns:
        set[str]: A set of stopwords to be removed.
    """
    if stoplist is None:
        return set()

    # User provides a list
    if isinstance(stoplist, list):
        return set(stoplist)

    # User provides a file path
    if isinstance(stoplist, str):
        if not os.path.isfile(stoplist):
            raise FileNotFoundError(f"Stoplist file not found: {stoplist}")
        with open(stoplist, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}

    raise TypeError("Stoplist must be None, a list, or a string path.")


def write_csv(rows, header, output_path):
    """
    Write a list of dictionaries or lists to a CSV file.

    Parameters:
        rows (list): List of rows (either dicts or lists).
        header (list[str]): Column names.
        output_path (str): Path where the CSV will be written.

    Returns:
        None
    """
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        for r in rows:
            if isinstance(r, dict):
                writer.writerow([r.get(col, "") for col in header])
            else:
                writer.writerow(r)
