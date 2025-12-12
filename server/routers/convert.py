from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from utils import save_upload_file, convert_to_pdf_libreoffice, cleanup_files, clean_filename_base
import os

router = APIRouter()

@router.post("/convert/word-to-pdf")
async def word_to_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(('.doc', '.docx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a Word document.")
    
    file_path = await save_upload_file(file)
    try:
        output_path = convert_to_pdf_libreoffice(file_path)
        background_tasks.add_task(cleanup_files, [file_path, output_path])
        
        final_filename = f"{clean_filename_base(file.filename)}-topdf.pdf"
        return FileResponse(
            output_path, 
            filename=final_filename, 
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename=\"{final_filename}\""}
        )
    except Exception as e:
        print(f"Error in word_to_pdf: {e}")
        cleanup_files([file_path])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert/excel-to-pdf")
async def excel_to_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel document.")
    
    file_path = await save_upload_file(file)
    try:
        output_path = convert_to_pdf_libreoffice(file_path)
        background_tasks.add_task(cleanup_files, [file_path, output_path])
        
        final_filename = f"{clean_filename_base(file.filename)}-topdf.pdf"
        return FileResponse(
            output_path, 
            filename=final_filename, 
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename=\"{final_filename}\""}
        )
    except Exception as e:
        print(f"Error in excel_to_pdf: {e}")
        cleanup_files([file_path])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert/ppt-to-pdf")
async def ppt_to_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(('.ppt', '.pptx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PowerPoint document.")
    
    file_path = await save_upload_file(file)
    try:
        output_path = convert_to_pdf_libreoffice(file_path)
        background_tasks.add_task(cleanup_files, [file_path, output_path])
        
        final_filename = f"{clean_filename_base(file.filename)}-topdf.pdf"
        return FileResponse(
            output_path, 
            filename=final_filename, 
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename=\"{final_filename}\""}
        )
    except Exception as e:
        print(f"Error in ppt_to_pdf: {e}")
        cleanup_files([file_path])
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text/to-pdf")
async def text_to_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a Text file.")
        
    file_path = await save_upload_file(file)
    try:
        output_path = convert_to_pdf_libreoffice(file_path)
        background_tasks.add_task(cleanup_files, [file_path, output_path])
        
        final_filename = f"{clean_filename_base(file.filename)}-topdf.pdf"
        return FileResponse(
            output_path, 
            filename=final_filename, 
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename=\"{final_filename}\""}
        )
    except Exception as e:
        print(f"Error in text_to_pdf: {e}")
        cleanup_files([file_path])
        raise HTTPException(status_code=500, detail=str(e))
