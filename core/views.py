from django.contrib.auth.forms import UserCreationForm
# pyrefly: ignore [missing-import]
from django.shortcuts import render, redirect, get_object_or_404
# pyrefly: ignore [missing-import]
from django.contrib.auth import authenticate, login, logout
# pyrefly: ignore [missing-import]
from django.contrib.auth.decorators import login_required
# pyrefly: ignore [missing-import]
from django_otp import match_token
# pyrefly: ignore [missing-import]
from rest_framework.views import APIView
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
# pyrefly: ignore [missing-import]
from rest_framework import status
# pyrefly: ignore [missing-import]
from rest_framework.authentication import TokenAuthentication
# pyrefly: ignore [missing-import]
from rest_framework.permissions import IsAuthenticated
#importação e validação para cadastro de dependente
# pyrefly: ignore [missing-import]
from django.contrib import messages
from .forms import DependentForm
# Importação centralizada e unificada dos seus modelos e serializers
from .models import ChildProfile, NavigationLog, AlertWord
from .serializers import NavigationLogSerializer
import qrcode
import base64
from io import BytesIO
# pyrefly: ignore [missing-import]
from django_otp.plugins.otp_totp.models import TOTPDevice
import secrets

# View da API REST (Recebe dados da extensão)
class LogAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # A extensão do navegador precisa enviar o token do filho específico (agent_token)
        agent_token = request.data.get('agent_token')
        
        try:
            # Encontra qual dependente está enviando a informação
            filho = ChildProfile.objects.get(agent_token=agent_token)
        except ChildProfile.DoesNotExist:
            return Response({'erro': 'Token do dependente inválido'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Copia os dados para inserir a categorização
        dados = request.data.copy()
        url = dados.get('url', '').lower()
        titulo = dados.get('title', '').lower()
        
        # Lógica de Categorização Dinâmica
        categoria_definida = 'Geral'
        
        # 1. Verifica se bate com as Palavras de Alerta (Alto Risco) definidas pelo Pai
        palavras_pai = AlertWord.objects.filter(parent=filho.parent)
        for alerta in palavras_pai:
            if alerta.word in url or alerta.word in titulo:
                categoria_definida = 'Alto Risco'
                break
                
        # 2. Se não for alto risco, aplica a inteligência padrão
        if categoria_definida != 'Alto Risco':
            termos_estudo = ['wikipedia', 'google', 'github', 'canvas']
            termos_entretenimento = ['youtube', 'netflix', 'tiktok', 'roblox']
            
            if any(termo in url or termo in titulo for termo in termos_estudo):
                categoria_definida = 'Estudo'
            elif any(termo in url or termo in titulo for termo in termos_entretenimento):
                categoria_definida = 'Entretenimento'
                
        dados['category'] = categoria_definida
        
        # Salva no banco de dados
        serializer = NavigationLogSerializer(data=dados)
        if serializer.is_valid():
            serializer.save(child=filho)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View da tela de Login
def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        codigo_2fa = request.POST.get('token_2fa') # Campo de 6 dígitos
        
        user = authenticate(request, username=usuario, password=senha)
        
        if user is not None:
            # Verifica se o usuário tem 2FA configurado e se o código está certo
            dispositivo = match_token(user, codigo_2fa)
            
            # Se o código estiver correto (ou se for o primeiro acesso sem 2FA criado ainda)
            if dispositivo or not user.totpdevice_set.exists():
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'login.html', {'erro': 'Código 2FA inválido.'})
        else:
            return render(request, 'login.html', {'erro': 'Usuário ou senha incorretos.'})
            
    return render(request, 'login.html')


# View do Dashboard Interno (Protegida)
@login_required(login_url='login')
def dashboard_view(request):
    # Regra 1: Se o formulário do Dashboard enviou uma nova palavra de alerta
    if request.method == 'POST' and 'add_word' in request.POST:
        palavra = request.POST.get('word')
        if palavra:
            # Salva no banco convertendo para letras minúsculas e tirando espaços extras
            AlertWord.objects.create(parent=request.user, word=palavra.strip().lower())
            return redirect('dashboard')

    # Regra 2: Busca todos os dados do banco para desenhar a tela
    dependentes = ChildProfile.objects.filter(parent=request.user)
    logs = NavigationLog.objects.filter(child__in=dependentes).order_by('-timestamp')[:50]
    palavras_alerta = AlertWord.objects.filter(parent=request.user)
    
    contexto = {
        'dependentes': dependentes,
        'logs': logs,
        'palavras_alerta': palavras_alerta
    }
    return render(request, 'dashboard.html', contexto)

@login_required
def register_dependent(request):
    if request.method == 'POST':
        form = DependentForm(request.POST)
        if form.is_valid():
            dependent = form.save(commit=False)
            dependent.parent = request.user 
            
            # A geração do token DEVE estar exatamente aqui
            dependent.agent_token = secrets.token_hex(32) 
            
            dependent.save()
            
            messages.success(request, 'Dependente cadastrado com sucesso!')
            return redirect('dashboard')
    else:
        form = DependentForm()
        
    return render(request, 'core/register_dependent.html', {'form': form})

@login_required
def delete_dependent(request, id):
    # O get_object_or_404 com 'parent=request.user' garante o isolamento da conta familiar[cite: 1]
    dependent = get_object_or_404(ChildProfile, id=id, parent=request.user)
    
    if request.method == 'POST':
        dependent.delete()
        
    return redirect('dashboard')

# View para o botão de Sair
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def setup_2fa_view(request):
    # Busca ou cria um dispositivo 2FA para o usuário logado
    device, created = TOTPDevice.objects.get_or_create(user=request.user, name="Smartphone do Usuário")
    
    # Obtém a URL oficial de configuração (authenticator protocol)
    url = device.config_url
    
    # Transforma a URL em uma imagem QR Code legível em Base64
    img = qrcode.make(url)
    buffer = BytesIO()
    # pyrefly: ignore [unexpected-keyword]
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    return render(request, 'setup_2fa.html', {'qr_code': qr_code_base64})

    # View para cadastro de novos responsáveis
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso! Faça o login.')
            return redirect('login')
    else:
        form = UserCreationForm()
        
    return render(request, 'registro.html', {'form': form})