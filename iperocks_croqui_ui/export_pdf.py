import os

from fpdf import FPDF
from PIL import Image


def sanitize_filename(text):
    """Sanitize text for use in filenames."""
    return text.replace(" ", "_").replace("/", "_").replace("\\", "_")


def generate_filename(sector, block, grade):
    """Generate a filename based on selected filters."""
    sector = sanitize_filename(sector) if sector else "All"
    block = sanitize_filename(block) if block else "All"
    grade = sanitize_filename(grade) if grade else "All"
    return f"routes_{sector}_{block}_{grade}.pdf"


class CustomPDF(FPDF):
    def __init__(self, page_format):
        super().__init__()
        self.page_format = page_format

    def add_page(self):
        super().add_page(orientation="L")  # Landscape orientation
        self.set_page_format(self.page_format)

    def set_page_format(self, page_format):
        self.w, self.h = page_format
        self.l_margin = self.r_margin = 10
        self.t_margin = self.b_margin = 10


def export_to_pdf(
    filtered_routes, image_folder, output_directory, sector=None, block=None, grade=None
):
    """
    Export a PDF composed of images corresponding to the filtered routes.

    Parameters:
    - filtered_routes (list): List of filtered route dictionaries.
    - image_folder (str): Directory containing the route images.
    - output_directory (str): Directory to save the output PDF.
    - sector (str, optional): Selected sector for filtering.
    - block (str, optional): Selected block for filtering.
    - grade (str, optional): Selected grade for filtering.
    """
    # Generate the output PDF filename based on filters
    output_pdf_filename = generate_filename(sector, block, grade)
    output_pdf_path = os.path.join(output_directory, output_pdf_filename)

    # PowerPoint slide dimensions in mm (landscape)
    slide_width_mm = 254
    slide_height_mm = 191

    # Page size in pixels at 96 DPI
    slide_width_px = int(slide_width_mm / 25.4 * 96)
    slide_height_px = int(slide_height_mm / 25.4 * 96)

    pdf = CustomPDF(page_format=(slide_width_mm, slide_height_mm))

    for route in filtered_routes:
        # Get the page number from the route
        page_number = route.get("page_number")
        if page_number is not None:
            # Construct the image filename
            image_filename = f"page_{page_number}.png"  # Adjust this pattern if needed
            image_path = os.path.join(image_folder, image_filename)

            # Check if the image file exists
            if os.path.exists(image_path):
                try:
                    # Open the image using PIL
                    with Image.open(image_path) as img:
                        # Ensure the image is in RGB mode
                        if img.mode != "RGB":
                            img = img.convert("RGB")

                        # Save the image to a temporary file in JPEG format (required by FPDF)
                        temp_image_path = f"temp_page_{page_number}.jpg"
                        img.save(temp_image_path, quality=95)  # Save with high quality

                        # Get image size (width and height)
                        width, height = img.size

                        # Calculate scaling to fit image into PDF page size
                        scale_width = slide_width_px / width
                        scale_height = slide_height_px / height
                        scale = min(scale_width, scale_height)

                        # New dimensions for the image
                        new_width = width * scale
                        new_height = height * scale

                        # Add a page to the PDF
                        pdf.add_page()

                        # Center image on page
                        x_offset = (
                            slide_width_mm - (new_width / 96 * 25.4)
                        ) / 2  # Convert pixels to mm
                        y_offset = (
                            slide_height_mm - (new_height / 96 * 25.4)
                        ) / 2  # Convert pixels to mm

                        # Add the image to the PDF
                        pdf.image(
                            temp_image_path,
                            x=x_offset,
                            y=y_offset,
                            w=new_width / 96 * 25.4,
                            h=new_height / 96 * 25.4,
                        )

                        # Remove the temporary image file
                        os.remove(temp_image_path)

                except Exception as e:
                    print(f"Error processing image {image_filename}: {e}")

    # Output the PDF
    pdf.output(output_pdf_path)
    return output_pdf_path
