from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from utils import (
    save_upload_file, 
    image_to_pdf, 
    convert_image_format, 
    pdf_to_images,
    create_zip_from_files,
    cleanup_files,
    clean_filename_base
)
import os

router = APIRouter()

@router.post("/image/to-pdf")
async def images_to_pdf_conversion(background_tasks: BackgroundTasks, file: List[UploadFile] = File(...)):
    saved_paths = []
    for f in file:
        if not f.content_type.startswith('image/'):
             raise HTTPException(status_code=400, detail=f"File {f.filename} is not an image.")
        saved_paths.append(await save_upload_file(f))
        
    try:
        output_path = image_to_pdf(saved_paths)
        background_tasks.add_task(cleanup_files, saved_paths + [output_path])
        
        # Use first image name as base
        base_name = clean_filename_base(file[0].filename)
        final_filename = f"{base_name}-imagestopdf.pdf"
        
        return FileResponse(
            output_path, 
            filename=final_filename, 
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename=\"{final_filename}\""}
        )
    except Exception as e:
        cleanup_files(saved_paths)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image/convert")
async def convert_image(background_tasks: BackgroundTasks, file: UploadFile = File(...), format: str = Form("PNG")):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
        
    valid_formats = ['JPEG', 'PNG', 'WEBP', 'BMP', 'GIF']
    if format.upper() not in valid_formats:
        raise HTTPException(status_code=400, detail=f"Format must be one of {valid_formats}")
        
    file_path = await save_upload_file(file)
    try:
        output_path = convert_image_format(file_path, format)
        background_tasks.add_task(cleanup_files, [file_path, output_path])
        
        final_filename = f"{clean_filename_base(file.filename)}-converted.{format.lower()}"
        
        return FileResponse(
            output_path, 
            filename=final_filename, 
            media_type=f'image/{format.lower()}',
            headers={"Content-Disposition": f"attachment; filename=\"{final_filename}\""}
        )
    except Exception as e:
        cleanup_files([file_path])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdf/to-images")
async def pdf_to_imgs(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
        
    file_path = await save_upload_file(file)
    try:
        image_paths = pdf_to_images(file_path)
        
        base_name = clean_filename_base(file.filename)
        zip_name = f"{base_name}-toimages.zip"
        
        zip_path = create_zip_from_files(image_paths, zip_name)
        background_tasks.add_task(cleanup_files, [file_path, zip_path] + image_paths)
        
        return FileResponse(
            zip_path, 
            filename=zip_name, 
            media_type='application/zip',
            headers={"Content-Disposition": f"attachment; filename=\"{zip_name}\""}
        )
    except Exception as e:
        cleanup_files([file_path])
        raise HTTPException(status_code=500, detail=str(e))
