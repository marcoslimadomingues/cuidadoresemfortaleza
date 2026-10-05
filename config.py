"""Dados da agência. Preencha TUDO antes de publicar (o build avisa o que falta)."""

NAME = "[NOME DA AGÊNCIA]"
CITY = "[CIDADE]"
REGION = "[REGIÃO]"
DOMAIN = "https://www.exemplo.com.br"   # sem barra final
WHATSAPP = "5585900000000"              # só dígitos, com 55 + DDD
PHONE = "(85) 0000-0000"
PHONE_E164 = "+558500000000"
EMAIL = "contato@exemplo.com.br"
ADDRESS = {
    "street": "[ENDEREÇO]",
    "city": "[CIDADE]",
    "state": "CE",
    "postal": "00000-000",
    "country": "BR",
}
CNPJ = "[CNPJ]"
HOURS = "Atendimento de segunda a sábado"   # ajuste ao real

# Perfis oficiais (só preencha os que existem; entram no schema sameAs)
SOCIAL = {
    "Google Business Profile": "",
    "Instagram": "",
    "Facebook": "",
    "LinkedIn": "",
    "YouTube": "",
}

# IDs de analytics (vazio = não carrega nada)
GA4_ID = ""            # ex.: G-XXXXXXXXXX
SEARCH_CONSOLE_TOKEN = ""   # meta google-site-verification

# Só preencha com dados REAIS e comprováveis. Vazio = a seção não aparece.
TESTIMONIALS = []      # [{"text": "...", "author": "Nome, cidade"}]
FACTS = []             # [("12 anos", "de atuação")]  — somente se verdadeiro

# Cidades atendidas (páginas locais em content.CITIES)
