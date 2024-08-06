import json
import os
import re
from typing import Dict, List, Optional

import pytesseract
from dotenv import load_dotenv
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from pdf2image import convert_from_path
from PIL import Image

load_dotenv(override=True)


class Route(BaseModel):
    id_number: int = Field(description="Route number id")
    name: str = Field(description="Name of the route")
    grade: str = Field(description="Route grade, e.g., V0, V10")
    description: str = Field(description="Describe how to start and climb the route")
    page_number: int = Field(description="Page where this route is described")
    block: str = Field(description="Name of the Boulder/block.")
    sector: str = Field(description="Name of the section where the boulder is located")


class CroquiPage(BaseModel):
    page_message: Optional[str] = Field(
        description="Any page-level text, warnigs, info, etc", default=""
    )
    routes: Optional[List[Route]] = Field(
        description="A list of routes", default_factory=lambda x: []
    )


prompt = PromptTemplate.from_template(
    """you receive the text version of a pdf page. Your task is to organize 
    the text and output in JSON. The page contains the block name in portugues 
    'Bloco', the sector (e.g., 'Setor Seu Luiz') some warnings or instructions, followed by a list of climbing 
    routes: with a id number, a name, a grade. Each of those should become a 
    separate item in the JSON output, including the page number

    Page content: 
    {page_content}

    page number: {page_number}

    Output format: 
    {output_format}
    """
)

pydantic_parser = PydanticOutputParser(pydantic_object=CroquiPage)
prompt = prompt.partial(output_format=pydantic_parser.get_format_instructions())

llm = ChatOpenAI(model="gpt-4o-mini")
json_parser = JsonOutputParser()

chain = prompt | llm | json_parser


def sanitize_filename(filename):
    # Remove invalid characters for a folder name
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", filename)


def pdf_to_png_and_extract_text(pdf_path, output_root, page_numbers=None):
    # Extract the base name of the PDF file (without extension)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    # Sanitize the base name to make it a valid folder name
    sanitized_name = sanitize_filename(base_name)
    # Define the output folder path
    output_folder = os.path.join(output_root, sanitized_name)

    # Convert PDF pages to images
    pages = convert_from_path(pdf_path)

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Initialize text storage
    text_storage = {}

    # Determine pages to process
    if page_numbers is None:
        page_indices = range(len(pages))
    else:
        page_indices = [p - 1 for p in page_numbers if 1 <= p <= len(pages)]

    # Save each page as a PNG image and extract text
    for i in page_indices:
        # Define output file paths
        image_path = os.path.join(output_folder, f"page_{i + 1}.png")
        text_path = os.path.join(output_folder, f"page_{i + 1}.txt")
        json_path = os.path.join(output_folder, f"page_{i + 1}.json")

        # Check if image file exists
        if not os.path.exists(image_path):
            # Save the page as a PNG image
            pages[i].save(image_path, "PNG")

        # Check if text file exists
        if os.path.exists(text_path):
            # Read text from the existing file
            with open(text_path, "r", encoding="utf-8") as text_file:
                text = text_file.read()
        else:
            # Extract text from the image using OCR
            text = pytesseract.image_to_string(pages[i])
            # Save the extracted text to a file
            with open(text_path, "w", encoding="utf-8") as text_file:
                text_file.write(text)

        # Store text in the dictionary
        text_storage[f"page_{i + 1}"] = text

        try:
            # Generate JSON response (assuming chain.invoke() is a valid function)
            response = chain.invoke({"page_content": text, "page_number": i + 1})

            # Save the response to a JSON file
            if not os.path.exists(json_path):
                with open(json_path, "w", encoding="utf-8") as json_file:
                    json.dump(response, json_file, indent=4)
        except OutputParserException:
            print(f"Page {i+1} doesn't contain expected information, skipping.")

    return text_storage
