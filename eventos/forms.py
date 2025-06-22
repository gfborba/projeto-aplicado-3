from django import forms
from .models import Evento

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nomeEvento', 'dataEvento', 'localEvento', 'descricaoEvento']
        widgets = {
            'dataEvento': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'descricaoEvento': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'nomeEvento': 'Nome do Evento',
            'dataEvento': 'Data e Hora',
            'localEvento': 'Local',
            'descricaoEvento': 'Descrição',
        }