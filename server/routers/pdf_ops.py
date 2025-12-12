from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from utils import (
    save_upload_file, 
    merge_pdfs, 
    split_pdf, 
    compress_pdf, 
    remove_pdf_pages,
    create_zip_from_files,
    cleanup_files,
    clean_filename_base
)
import os
import json

router = APIRouter()

@router.post("/pdf/merge")
async def merge_pdf_files(background_tasks: BackgroundTasks, file: List[UploadFile] = File(...)):
    saved_paths = []
    for f in file:
        if not f.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {f.filename} is not a PDF.")
        saved_paths.append(await save_upload_file(f))
        
    try:
        output_path = merge_pdfs(saved_paths)
        background_tasks.add_task(cleanup_files, saved_paths + [output_path])
        
        # Use first file name as base for proper naming
        base_name = clean_filename_base(file[0].filename)
        final_filename = f"{base_name}-merged.pdf"
        
        return FileResponse(
            output_path, 
            filename=final_filename, 
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename=\"{final_filename}\""}
        )
    except Exception as e:
        cleanup_files(saved_paths)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdf/split")
async def split_pdf_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
        
    file_path = await save_upload_file(file)
    try:
        split_files = split_pdf(file_path)
        
        base_name = clean_filename_base(file.filename)
        zip_name = f"{base_name}-split.zip"
        
        zip_path = create_zip_from_files(split_files, zip_name)
        # Cleanup original, split parts, and zip
        background_tasks.add_task(cleanup_files, [file_path, zip_path] + split_files)
        
        return FileResponse(
            zip_path, 
            filename=zip_name, 
            media_type='application/zip',
            headers={"Content-Disposition": f"attachment; filename=\"{zip_name}\""}
        )
    except Exception as e:
        cleanup_files([file_path])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdf/compress")
async def compress_pdf_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
        
    file_path = await save_upload_file(file)
    try:
        output_path = compress_pdf(file_path)
        background_tasks.add_task(cleanup_files, [file_path, output_path])
        
        final_filename = f"{clean_filename_base(file.filename)}-compressed.pdf"
        
        return FileResponse(
            output_path, 
            filename=final_filename, 
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename=\"{final_filename}\""}
        )
    except Exception as e:
        cleanup_files([file_path])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdf/remove-pages")
async def remove_pages(background_tasks: BackgroundTasks, file: UploadFile = File(...), pages: str = Form("[]")):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
        
    try:
        pages_list = json.loads(pages)
        if not isinstance(pages_list, list):
            raise ValueError
    except:
        raise HTTPException(status_code=400, detail="Pages must be a JSON list of integers.")
        
    file_path = await save_upload_file(file)
    try:
        output_path = remove_pdf_pages(file_path, pages_list)
        background_tasks.add_task(cleanup_files, [file_path, output_path])
        
        final_filename = f"{clean_filename_base(file.filename)}-pages-removed.pdf"
        
        return FileResponse(
            output_path, 
            filename=final_filename, 
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename=\"{final_filename}\""}
        )
    except Exception as e:
        cleanup_files([file_path])
        raise HTTPException(status_code=500, detail=str(e))
