import os
import subprocess
import uuid
import shutil
from typing import List
from fastapi import UploadFile
import PyPDF2
from PIL import Image
import img2pdf
import pdf2image

# Configuration
import tempfile
import os

UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "uploads")
OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "outputs")
def get_libreoffice_command():
    import platform
    if platform.system() == "Windows":
        # Common installation paths for LibreOffice on Windows
        possible_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        # Fallback to just 'soffice' if not found in standard locations
        return "soffice"
    # Linux/Mac default
    return "libreoffice"

LIBREOFFICE_CMD = get_libreoffice_command()

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_unique_filename(original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4()}{ext}"

def clean_filename_base(filename: str) -> str:
    """
    Returns a cleaned base filename (lowercase, spaces to hyphens) without extension.
    """
    base = os.path.splitext(filename)[0]
    return base.lower().strip().replace(" ", "-")

async def save_upload_file(upload_file: UploadFile) -> str:
    filename = generate_unique_filename(upload_file.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path

def convert_to_pdf_libreoffice(input_path: str) -> str:
    """
    Converts docx, xlsx, pptx to PDF using LibreOffice.
    Returns the path to the generated PDF.
    """
    # Ensure absolute paths
    input_path = os.path.abspath(input_path)
    output_temp_dir = os.path.abspath(OUTPUT_DIR)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    cmd = [
        LIBREOFFICE_CMD,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        output_temp_dir,
        input_path
    ]
    
    # print(f"Executing command: {' '.join(cmd)}")  # Debug logging

    try:
        # Check if LibreOffice executable exists before running
        # (This avoids a confusing FileNotFoundError from subprocess if the binary is missing)
        # Note: If LIBREOFFICE_CMD is just 'soffice', shutil.which can check it.
        if os.path.isabs(LIBREOFFICE_CMD) and not os.path.exists(LIBREOFFICE_CMD):
             raise Exception(f"LibreOffice executable not found at: {LIBREOFFICE_CMD}")

        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # LibreOffice saves the file with the same basename in output dir
        basename = os.path.basename(input_path)
        filename_no_ext = os.path.splitext(basename)[0]
        output_path = os.path.join(output_temp_dir, f"{filename_no_ext}.pdf")
        
        if not os.path.exists(output_path):
            # Sometimes LibreOffice might output with a different name or fail silently.
            # Check for any PDF created recently? No, let's trust the name.
            raise Exception(f"Output PDF not found at {output_path} after conversion.\nscostdout: {result.stdout.decode()}\nstderr: {result.stderr.decode()}")
            
        return output_path
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else "Unknown error"
        print(f"LibreOffice conversion failed: {error_msg}")
        raise Exception(f"LibreOffice conversion failed with error: {error_msg}")
    except Exception as e:
        print(f"Conversion error: {str(e)}")
        raise e

def merge_pdfs(file_paths: List[str]) -> str:
    merger = PyPDF2.PdfMerger()
    for path in file_paths:
        merger.append(path)
    
    output_filename = f"merged_{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    merger.write(output_path)
    merger.close()
    return output_path

def split_pdf(file_path: str, output_dir: str = OUTPUT_DIR) -> List[str]:
    # Returns a list of paths to the split files (or a zip? For now let's say we return a zip path ideally,
    # but the requirement says "Split PDF". Usually this returns a ZIP of PDFs. 
    # For simplicity in this function, let's just return the list of created files.)
    # Actually, for the API, we probably want to return a ZIP file containing all pages.
    
    reader = PyPDF2.PdfReader(file_path)
    created_files = []
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    for i, page in enumerate(reader.pages):
        writer = PyPDF2.PdfWriter()
        writer.add_page(page)
        
        out_filename = f"{base_name}_page_{i+1}.pdf"
        out_path = os.path.join(output_dir, out_filename)
        
        with open(out_path, "wb") as f:
            writer.write(f)
        created_files.append(out_path)
        
    return created_files

def compress_pdf(file_path: str) -> str:
    reader = PyPDF2.PdfReader(file_path)
    writer = PyPDF2.PdfWriter()
    
    for page in reader.pages:
        page.compress_content_streams() # Basic compression
        writer.add_page(page)
    
    # Enable compression in writer
    for page in writer.pages:
        page.compress_content_streams()
        
    output_filename = f"compressed_{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    with open(output_path, "wb") as f:
        writer.write(f)
        
    return output_path

def remove_pdf_pages(file_path: str, pages_to_remove: List[int]) -> str:
    # pages_to_remove is 1-based index list
    reader = PyPDF2.PdfReader(file_path)
    writer = PyPDF2.PdfWriter()
    
    for i, page in enumerate(reader.pages):
        if (i + 1) not in pages_to_remove:
            writer.add_page(page)
            
    output_filename = f"edited_{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    with open(output_path, "wb") as f:
        writer.write(f)
        
    return output_path

def image_to_pdf(image_paths: List[str]) -> str:
    # Use img2pdf for better quality or PIL
    # img2pdf is good for exact embedding suitable for photos/scans
    # If images have different sizes, img2pdf handles it well.
    
    output_filename = f"images_{uuid.uuid4()}.pdf"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    with open(output_path, "wb") as f:
        # img2pdf.convert wants bytes or filenames
        f.write(img2pdf.convert(image_paths))
        
    return output_path

def convert_image_format(input_path: str, format: str) -> str:
    # format: 'PNG', 'JPEG', etc.
    img = Image.open(input_path)
    # Convert to RGB if saving as JPEG
    if format.upper() == 'JPEG' and img.mode != 'RGB':
        img = img.convert('RGB')
        
    output_filename = f"{os.path.splitext(os.path.basename(input_path))[0]}.{format.lower()}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    img.save(output_path, format=format.upper())
    return output_path

def pdf_to_images(file_path: str) -> List[str]:
    # Returns list of image paths.
    # Requires poppler installed for pdf2image.
    # User didn't specify poppler, but pdf2image needs it. I will assume it's there or give instructions.
    
    try:
        images = pdf2image.convert_from_path(file_path)
        output_paths = []
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        for i, img in enumerate(images):
            out_name = f"{base_name}_page_{i+1}.jpg"
            out_path = os.path.join(OUTPUT_DIR, out_name)
            img.save(out_path, 'JPEG')
            output_paths.append(out_path)
            
        return output_paths
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        raise e


def create_zip_from_files(file_paths: List[str], zip_name: str) -> str:
    zip_path = os.path.join(OUTPUT_DIR, zip_name)
    from zipfile import ZipFile
    with ZipFile(zip_path, 'w') as zipf:
        for file in file_paths:
            zipf.write(file, os.path.basename(file))
    return zip_path

def cleanup_files(file_paths: List[str]):
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Error cleaning up {path}: {e}")
