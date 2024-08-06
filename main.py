import argparse
import os

from iperocks_croqui_ui.pdf_converter import pdf_to_png_and_extract_text


def parse_page_ranges(pages, total_pages=200):
    """
    Convert a page range string like '1-5,6,7' into a list of page indices.
    """
    pages_set = set()
    if pages:
        ranges = pages.split(",")

        for r in ranges:
            if "-" in r:
                start, end = r.split("-")
                try:
                    pages_set.update(range(int(start), int(end) + 1))
                except ValueError:
                    print(f"Error: Invalid page range '{r}'.")
                    exit(1)
            else:
                try:
                    pages_set.add(int(r))
                except ValueError:
                    print(f"Error: Invalid page number '{r}'.")
                    exit(1)

    # Ensure pages are within valid range
    return sorted(p for p in pages_set if 1 <= p <= total_pages)


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Convert PDF pages to PNG images.")
    parser.add_argument(
        "--pdf-filename",
        type=str,
        required=True,
        help="The name of the PDF file (with extension) in the assets folder.",
    )
    parser.add_argument(
        "-o",
        "--output-folder",
        type=str,
        default="output",
        help="Folder to save the output images.",
    )
    parser.add_argument(
        "-p",
        "--pages",
        type=str,
        default=None,
        help="Comma-separated list of page numbers to convert (e.g., '1,2,5-10').",
    )

    # Parse arguments
    args = parser.parse_args()

    # Check if the PDF file exists
    if not os.path.isfile(args.pdf_filename):
        print(f"Error: PDF file '{args.pdf_filename}' not found.")
        exit(1)

    # Parse page numbers
    page_numbers = parse_page_ranges(args.pages)

    # Convert the PDF to PNG images
    pdf_to_png_and_extract_text(args.pdf_filename, args.output_folder, page_numbers)


if __name__ == "__main__":
    main()
