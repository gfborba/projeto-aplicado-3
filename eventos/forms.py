from django import forms
from .models import Evento, Pergunta, Resposta, AvaliacaoFornecedor

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

class PerguntaForm(forms.ModelForm):
    class Meta:
        model = Pergunta
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Digite sua pergunta sobre este evento...',
                'class': 'form-control'
            }),
        }
        labels = {
            'texto': ''
        }

class RespostaForm(forms.ModelForm):
    class Meta:
        model = Resposta
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Digite sua resposta...',
                'class': 'form-control'
            }),
        }
        labels = {
            'texto': ''
        }
        
class AvaliacaoFornecedorForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoFornecedor
        fields = ['nota', 'comentario']
        widgets = {
            'nota': forms.Select(attrs={
                'class': 'form-select',
            }),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Deixe um comentário opcional...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nota'].widget.choices = AvaliacaoFornecedor.NOTA_CHOICES