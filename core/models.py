# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.contrib.auth.models import User

# Tabela 1: Perfil do Dependente (Filho)
class ChildProfile(models.Model):
    # Relaciona o filho a um usuário pai (administrador da conta)
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100, verbose_name="Nome do Filho")
    # Token de API que a extensão do navegador vai usar para enviar os dados
    agent_token = models.CharField(max_length=64, unique=True) 

    def __str__(self):
        return self.name

# Tabela 2: Histórico de Navegação
class NavigationLog(models.Model):
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='logs')
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=255, null=True, blank=True)
    # Categoria automática: Estudo, Entretenimento, Alto Risco, Geral
    category = models.CharField(max_length=50, default='Geral')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.child.name} acessou {self.title}"
       
# Tabela 3: Palavras de Alerta Customizadas pelo Pai
class AlertWord(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alert_words')
    word = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Alerta: {self.word}"