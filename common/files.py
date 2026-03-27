import hashlib

from fastapi import HTTPException, UploadFile, status

from common.settings import get_settings


ALLOWED_EXTS = {".txt", ".pdf", ".docx"}


def ensure_upload_allowed(file: UploadFile) -> None:
    settings = get_settings()
    filename = file.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的文件格式")

    size = getattr(file, "size", None)
    if size is not None:
        if size > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件过大")


async def calc_md5(file: UploadFile) -> str:
    h = hashlib.md5()
    await file.seek(0)
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        h.update(chunk)
    await file.seek(0)
    return h.hexdigest()
