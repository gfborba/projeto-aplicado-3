from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Avaliacao



@login_required(login_url='login')
def index(request):
    return render(request, 'index.html')

def avaliacao(request, id):
    ja_avaliou = Avaliacao.objects.filter(
        user=request.user
    ).exists()

    if ja_avaliou:
        return render(request, 'index.html', {
        })

    if request.method == "POST":
        nota = request.POST.get('nota')
        comentario = request.POST.get('comentario')
        Avaliacao.objects.create(
            user=request.user,
            nota=nota,
            comentario=comentario
        )
        return redirect('index')
    else:
        return render(request, 'avaliar.html')