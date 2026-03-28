from django import forms


class ResultPasteForm(forms.Form):
    result_text = forms.CharField(
        label='ChatGPTの結果',
        widget=forms.Textarea(attrs={'rows': 16, 'class': 'form-control', 'placeholder': 'ChatGPTの結果を貼り付けてください'})
    )
