import json
import hashlib

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.http import Http404
from django.core.exceptions import PermissionDenied

from .forms import ResultPasteForm

from .models import OpenProcessingLog, OutputQualityCheck
from .services import (
    list_prompt_files,
    get_prompt_file,
    move_to_processing,
    parse_prompt,
    save_result_file,
    load_prompt_meta,
    run_output_quality_check,
)

import re
from django.contrib.auth import get_user_model

from accounts.models import UserProfile

User = get_user_model()

def extract_user_code(filename: str):
    m = re.search(r"_(\d{4})_prompt\.txt$", filename)
    return m.group(1) if m else None

def get_owner_by_filename(filename: str):
    user_code = extract_user_code(filename)
    if not user_code:
        return None

    profile = (
        UserProfile.objects
        .select_related("user")
        .filter(user_code=user_code)
        .first()
    )
    return profile.user if profile else None

def get_prompt_owner(filename: str):
    return (
        PromptFileOwner.objects
        .select_related("created_by")
        .filter(filename=filename)
        .first()
    )


def can_access_prompt_file(user, filename: str) -> bool:
    if user.is_staff or user.is_superuser:
        return True

    owner = get_prompt_owner(filename)
    return bool(owner and owner.created_by_id == user.id)


@login_required
@permission_required("accounts.can_execute_system", raise_exception=True)
def index(request):
    is_admin = request.user.is_staff or request.user.is_superuser

    files = []
    for row in list_prompt_files():
        owner = get_owner_by_filename(row["name"])

        if not is_admin:
            if owner != request.user:
                continue

        files.append({
            "name": row["name"],
            "mtime": row["mtime"],
            "size": row["size"],
            "owner_name": owner.get_full_name() or owner.username if owner else "-",
            "owner_code": owner.profile.user_code if owner and hasattr(owner, "profile") else "-",
        })

    return render(
        request,
        "open_app/index.html",
        {
            "files": files,
            "is_admin": is_admin,
        },
    )

@login_required
@permission_required("accounts.can_execute_system", raise_exception=True)
def prompt_detail(request, filename):
    try:
        path = get_prompt_file(filename)
    except FileNotFoundError:
        raise Http404("対象の prompt ファイルは存在しません")

    content = path.read_text(encoding="utf-8")
    parsed = parse_prompt(content)
    meta = load_prompt_meta(filename)

    quality_check = OutputQualityCheck.objects.filter(filename=parsed["output_filename"]).first()

    if request.method == "POST":
        form = ResultPasteForm(request.POST)
        if form.is_valid():
            result_text = form.cleaned_data["result_text"]
            check = run_output_quality_check(result_text, parsed, meta)

            OutputQualityCheck.objects.update_or_create(
                filename=parsed["output_filename"],
                defaults={
                    "has_error": check["has_error"],
                    "error_details": check["details"],
                    "check_score": check["score"],
                },
            )

            if check["has_error"]:
                messages.error(request, "検品で警告があります。内容を確認してください。")
            else:
                try:
                    move_to_processing(filename)
                except FileNotFoundError:
                    raise Http404("対象の prompt ファイルは存在しません")

                result_path = save_result_file(
                    request_no=parsed["request_no"],
                    filename=parsed["output_filename"],
                    result_text=result_text,
                    prompt_filename=filename,
                )

                result_meta = {
                    "request_no": parsed["request_no"],
                    "prompt_filename": filename,
                    "result_filename": result_path.name,
                    "hash_sha256": hashlib.sha256(result_text.encode("utf-8")).hexdigest(),
                    "quality_score": check["score"],
                    "quality_has_error": check["has_error"],
                    "quality_details": check["details"],
                }
                result_path.with_suffix(".json").write_text(
                    json.dumps(result_meta, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

                OpenProcessingLog.objects.create(
                    request_no=parsed["request_no"],
                    prompt_filename=filename,
                    result_filename=result_path.name,
                    processed_by=request.user,
                )
                messages.success(request, f"{result_path.name} をDMZへ保存しました。")
                return redirect("open_index")
    else:
        form = ResultPasteForm()

    back_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or ""

    return render(
        request,
        "open_app/detail.html",
        {
            "filename": filename,
            "parsed": parsed,
            "meta": meta,
            "form": form,
            "back_url": back_url,
            "quality_check": quality_check,
        },
    )

@login_required
@permission_required("accounts.can_execute_system", raise_exception=True)
def prompt_delete(request, filename):
    try:
        path = get_prompt_file(filename)
    except FileNotFoundError:
        raise Http404("対象の prompt ファイルは存在しません")

    owner = get_owner_by_filename(filename)

    if not (request.user.is_staff or request.user.is_superuser):
        if owner != request.user:
            raise PermissionDenied("この prompt ファイルを削除する権限がありません。")

    if request.method == "POST":
        path.unlink(missing_ok=True)
        messages.success(request, f"{filename} を削除しました。")
        return redirect("open_index")

    return render(
        request,
        "open_app/prompt_confirm_delete.html",
        {
            "filename": filename,
            "owner_name": owner.get_full_name() or owner.username if owner else "-",
        },
    )
