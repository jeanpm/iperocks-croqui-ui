import pdfplumber


def extract_page_text(pdf_path, page_number):
    with pdfplumber.open(pdf_path) as pdf:
        # Ensure the page number is within the PDF page range
        if page_number < 1 or page_number > len(pdf.pages):
            raise ValueError(
                f"Invalid page number: {page_number}. The PDF has {len(pdf.pages)} pages."
            )

        # Page numbers in pdfplumber are 0-indexed
        page = pdf.pages[page_number - 1]
        text = page.extract_text()
        return text


# Example usage
pdf_path = "assets/Croqui_Iperocks_v4-3.pdf"
page_number = 17  # The page you want to read

try:
    page_text = extract_page_text(pdf_path, page_number)
    print(page_text)
except ValueError as e:
    print(e)
