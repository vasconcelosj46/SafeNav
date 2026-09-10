// URLs e Tokens de Comunicação com a API
const API_URL = "http://127.0.0.1:8000/api/logs/";
const DRF_TOKEN = "COLOQUE_O_TOKEN_AQUI"; // Token de autenticação da API
const AGENT_TOKEN = "COLOQUE_O_AGENTE_AQUI"; // Token identificador do dependente (filho)

// Fica escutando atualizações nas abas do navegador
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // Só dispara se a página carregou completamente e se é um site web real (http/https)
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        
        // Monta o pacote de dados
        const logData = {
            agent_token: AGENT_TOKEN,
            url: tab.url,
            title: tab.title || "Página sem título"
        };

        // Envia o pacote para o backend via POST
        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${DRF_TOKEN}`
            },
            body: JSON.stringify(logData)
        })
        .then(response => {
            if (response.ok) {
                console.log("SafeNav: Log salvo com sucesso!");
            } else {
                console.error("SafeNav: Falha na autorização ou erro no servidor.");
            }
        })
        .catch(error => console.error("SafeNav: Erro de rede", error));
    }
});