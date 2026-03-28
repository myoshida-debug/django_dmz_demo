from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class OpenProcessingLog(models.Model):
    request_no = models.CharField(max_length=32, db_index=True)
    prompt_filename = models.CharField(max_length=255)
    result_filename = models.CharField(max_length=255)
    processed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    saved_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-saved_at']
        indexes = [
            models.Index(fields=['request_no', 'saved_at']),
        ]

    def __str__(self):
        return f'{self.request_no} by {self.processed_by}'

class PromptFileOwner(models.Model):
    filename = models.CharField(max_length=255, unique=True, db_index=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_prompt_files",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "open_prompt_file_owner"
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return self.filename


class OutputQualityCheck(models.Model):
    filename = models.CharField(max_length=255, unique=True, db_index=True)
    has_error = models.BooleanField(default=False)
    error_details = models.TextField(blank=True, default="")
    check_score = models.IntegerField(default=0)
    checked_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-checked_at"]

    def __str__(self):
        return f"{self.filename} / score={self.check_score}"
