from django import forms
from django.contrib.auth.models import User, Permission
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False, label='メールアドレス')
    last_name = forms.CharField(max_length=150, required=False, label='姓')
    first_name = forms.CharField(max_length=150, required=False, label='名')
    is_active = forms.BooleanField(required=False, initial=True, label='有効')

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'email', 'is_active', 'password1', 'password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'email', 'is_active', 'is_staff']
        labels = {
            'username': 'ユーザーID',
            'last_name': '姓',
            'first_name': '名',
            'email': 'メールアドレス',
            'is_active': '有効',
            'is_staff': '管理画面利用可',
        }


class UserPermissionForm(forms.Form):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='権限'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'].queryset = Permission.objects.filter(
            codename__in=[
                'can_view_system',
                'can_execute_system',
                'can_manage_users',
            ]
        ).select_related('content_type')
