from django import forms
from .models import Evento

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nomeEvento', 'dataEvento', 'localEvento', 'descricaoEvento', 'cep', 'previsao_participantes']
        widgets = {
            'nomeEvento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do evento'
            }),
            'dataEvento': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'localEvento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do local (ex: Centro de Eventos)'
            }),
            'descricaoEvento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva o evento...'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'id': 'cep'
            }),
            'previsao_participantes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 100',
                'min': '1',
                'max': '10000'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cep'].required = True