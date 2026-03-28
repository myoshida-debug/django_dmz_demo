from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomUserCreationForm, UserEditForm, UserPermissionForm


@login_required
@permission_required('accounts.can_manage_users', raise_exception=True)
def user_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
@permission_required('accounts.can_manage_users', raise_exception=True)
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'ユーザー「{user.username}」を登録しました。')
            return redirect('user_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'ユーザー登録',
    })


@login_required
@permission_required('accounts.can_manage_users', raise_exception=True)
def user_edit(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'ユーザー「{user_obj.username}」を更新しました。')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user_obj)

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'ユーザー編集',
        'target_user': user_obj,
    })


@login_required
@permission_required('accounts.can_manage_users', raise_exception=True)
def user_permissions(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UserPermissionForm(request.POST)
        if form.is_valid():
            selected_permissions = form.cleaned_data['permissions']
            user_obj.user_permissions.set(selected_permissions)
            messages.success(request, f'ユーザー「{user_obj.username}」の権限を更新しました。')
            return redirect('user_list')
    else:
        form = UserPermissionForm(initial={
            'permissions': user_obj.user_permissions.all()
        })

    return render(request, 'accounts/user_permissions.html', {
        'form': form,
        'target_user': user_obj,
    })


@login_required
@permission_required('accounts.can_view_system', raise_exception=True)
def protected_view_page(request):
    return render(request, 'accounts/protected_view_page.html')


@login_required
@permission_required('accounts.can_execute_system', raise_exception=True)
def protected_execute_page(request):
    if request.method == 'POST':
        messages.success(request, '実施処理を実行しました。')
        return redirect('protected_execute_page')

    return render(request, 'accounts/protected_execute_page.html')
