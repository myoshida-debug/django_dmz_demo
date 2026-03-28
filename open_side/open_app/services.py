from pathlib import Path
from django.conf import settings
from django.utils import timezone

import hashlib
import json
import re

def list_prompt_files():
    items = []
    for path in sorted(settings.DMZ_CLOSE_TO_OPEN_PENDING.glob('*_prompt.txt')):
        stat = path.stat()
        items.append({
            'name': path.name,
            'path': path,
            'size': stat.st_size,
            'mtime': timezone.datetime.fromtimestamp(stat.st_mtime, tz=timezone.get_current_timezone()),
        })
    return items


def move_to_processing(filename: str) -> Path:
    src = settings.DMZ_CLOSE_TO_OPEN_PENDING / filename
    dst = settings.DMZ_CLOSE_TO_OPEN_PROCESSING / filename
    if src.exists() and not dst.exists():
        src.rename(dst)
    return dst if dst.exists() else src

def get_prompt_file(filename: str) -> Path:
    processing = settings.DMZ_CLOSE_TO_OPEN_PROCESSING / filename
    pending = settings.DMZ_CLOSE_TO_OPEN_PENDING / filename
    if processing.exists():
        return processing
    if pending.exists():
        return pending
    raise FileNotFoundError(filename)


def parse_prompt(content: str) -> dict:
    request_no = ''
    doc_type = ''
    output_filename = ''
    header, _, body = content.partition('\n\n')
    for line in header.splitlines():
        if line.startswith('REQUEST_NO:'):
            request_no = line.split(':', 1)[1].strip()
        elif line.startswith('DOC_TYPE:'):
            doc_type = line.split(':', 1)[1].strip()
        elif line.startswith('OUTPUT_FILENAME:'):
            output_filename = line.split(':', 1)[1].strip()
    return {
        'request_no': request_no,
        'doc_type': doc_type,
        'output_filename': output_filename,
        'prompt_body': body.strip(),
    }


def save_result_file(request_no: str, filename: str, result_text: str, prompt_filename: str) -> Path:
    target = settings.DMZ_OPEN_TO_CLOSE_RETURNED / filename
    content = (
        f'REQUEST_NO: {request_no}\n'
        f'PROMPT_FILENAME: {prompt_filename}\n'
        f'SAVED_AT: {timezone.now().isoformat()}\n\n'
        f'{result_text.strip()}\n'
    )
    target.write_text(content, encoding='utf-8')
    processing_file = settings.DMZ_CLOSE_TO_OPEN_PROCESSING / prompt_filename
    if processing_file.exists():
        processing_file.unlink()
    return target


def get_prompt_meta_file(filename: str) -> Path:
    return get_prompt_file(filename).with_suffix(".json")


def load_prompt_meta(filename: str) -> dict:
    meta_file = get_prompt_meta_file(filename)
    if not meta_file.exists():
        return {}
    return json.loads(meta_file.read_text(encoding="utf-8"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_output_quality_check(result_text: str, parsed: dict, meta: dict) -> dict:
    errors = []
    score = 0

    if not result_text or len(result_text.strip()) < 20:
        errors.append("出力が短すぎます")
        score += 30

    for token in ["患者実名", "住所", "電話番号"]:
        if token in result_text:
            errors.append(f"禁止語を含む可能性: {token}")
            score += 20

    if "考えられる" in result_text:
        errors.append("推測表現が含まれています")
        score += 10

    if meta.get("document_type_display") and meta["document_type_display"] not in (parsed.get("doc_type") or ""):
        score += 5

    return {
        "has_error": bool(errors),
        "details": "\n".join(errors),
        "score": score,
    }
