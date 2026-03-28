from django.db import models


class SystemPermission(models.Model):
    """
    Django の Permission を発行するためのダミーモデル
    実データは持たず、権限定義だけに使う
    """
    name = models.CharField(max_length=50, default="system_permission")

    class Meta:
        verbose_name = "システム権限"
        verbose_name_plural = "システム権限"
        permissions = [
            ("can_view_system", "システムを閲覧できる"),
            ("can_execute_system", "匿名化・DMZ送信・取込・取消を実施できる"),
            ("can_manage_users", "ユーザーを管理できる"),
            ("can_manage_templates", "プロンプトテンプレートを管理できる"),
        ]

    def __str__(self):
        return self.name
