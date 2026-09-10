# pyrefly: ignore [missing-import]
from django import forms
from .models import ChildProfile

class DependentForm(forms.ModelForm):
    class Meta:
        model = ChildProfile
        fields = ['name'] 
        widgets = {
            'name': forms.TextInput(attrs={
                # Classes atualizadas para o padrão Tailwind
                'class': 'w-full px-4 py-2 border border-slate-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-600', 
                'placeholder': 'Ex: Joãozinho'
            }),
        }