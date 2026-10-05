"""Gerador estático. Uso: python build.py  ->  gera a pasta ./site"""
import html
import json
import shutil
import datetime
from pathlib import Path
from urllib.parse import quote

import config as C
from content import SERVICES, ARTICLES, CITIES, GLOBAL_FAQ, SCOPE_NOTE

ROOT = Path(__file__).parent
OUT = ROOT / "site"
TODAY = datetime.date.today().isoformat()
e = html.escape
SVC = {s["slug"]: s for s in SERVICES}
ART = {a["slug"]: a for a in ARTICLES}
PAGES = []  # (path, priority) para sitemap


# ------------------------------------------------------------ helpers
def wa(msg="Olá! Gostaria de solicitar um cuidador."):
    return f"https://wa.me/{C.WHATSAPP}?text={quote(msg)}"


def url(path):
    return f"{C.DOMAIN}/{path}/" if path else f"{C.DOMAIN}/"


def icon(name):
    paths = {
        "heart": "M12 21s-7-4.6-9.3-9A5.3 5.3 0 0 1 12 6a5.3 5.3 0 0 1 9.3 6c-2.3 4.4-9.3 9-9.3 9z",
        "shield": "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z M9 12l2 2 4-4",
        "clock": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M12 7v5l3 2",
        "home": "M3 11l9-8 9 8 M5 10v10h14V10",
        "users": "M16 11a3 3 0 1 0-6 0 3 3 0 0 0 6 0z M5 20c0-4 3-6 7-6s7 2 7 6",
        "check": "M5 12l5 5 9-10",
        "wa": "M3 21l1.6-5A9 9 0 1 1 8 19.5z",
    }
    return (f'<svg class="ic" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{paths[name]}"/></svg>')


def cta_btn(label, ev="cta_click", where="", primary=True, msg=None):
    cls = "btn btn-primary" if primary else "btn btn-ghost"
    return (f'<a class="{cls}" href="{e(wa(msg) if msg else wa())}" rel="noopener" target="_blank" '
            f'data-event="whatsapp_click" data-where="{e(where or ev)}">{icon("wa")}{e(label)}</a>')


def faq_block(items, heading="Perguntas frequentes"):
    rows = "".join(f'<details><summary>{e(q)}</summary><div class="ans"><p>{a}</p></div></details>' for q, a in items)
    return f'<section class="section" aria-labelledby="faq"><h2 id="faq">{heading}</h2><div class="faq">{rows}</div></section>'


def faq_schema(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in items]}


def strip_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s)


def quick_block(text):
    return f'<aside class="quick" aria-label="Resposta rápida"><p class="quick-label">Resposta rápida</p><p>{text}</p></aside>'


def breadcrumbs(crumbs):
    items = [("Início", "")] + crumbs
    li = []
    for i, (name, path) in enumerate(items):
        if i == len(items) - 1:
            li.append(f'<li aria-current="page">{e(name)}</li>')
        else:
            li.append(f'<li><a href="/{path + "/" if path else ""}">{e(name)}</a></li>')
    html_ = f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(li)}</ol></nav>'
    schema = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": url(p)} for i, (n, p) in enumerate(items)]}
    return html_, schema


def related_services(slugs, title="Você também pode precisar de"):
    cards = "".join(
        f'<a class="card" href="/{s}/"><h3>{e(SVC[s]["name"])}</h3><p>{e(SVC[s]["short"])}</p></a>' for s in slugs)
    return f'<section class="section"><h2>{title}</h2><div class="grid">{cards}</div></section>'


def related_articles(slugs, title="Conteúdos relacionados"):
    cards = "".join(
        f'<a class="card" href="/blog/{s}/"><span class="tag">{e(ART[s]["cluster"])}</span><h3>{e(ART[s]["title"])}</h3></a>'
        for s in slugs if s in ART)
    return f'<section class="section"><h2>{title}</h2><div class="grid">{cards}</div></section>' if cards else ""


def cta_band(title="Precisa de um cuidador? Fale conosco.", text="Conte a situação da sua família. Indicamos o profissional adequado e orientamos os próximos passos."):
    return (f'<section class="cta-band"><div class="wrap"><h2>{e(title)}</h2><p>{e(text)}</p>'
            f'<div class="actions">{cta_btn("Solicitar orçamento pelo WhatsApp", where="band")}'
            f'<a class="btn btn-light" href="/contato/" data-event="cta_click" data-where="band_form">Solicitar atendimento</a></div></div></section>')


def lead_form(idp="f"):
    opts = "".join(f"<option>{e(s['name'])}</option>" for s in SERVICES) + "<option>Ainda não sei</option>"
    cities = "".join(f"<option>{e(c['name'])}</option>" for c in CITIES) + "<option>Outra cidade</option>"
    return f'''<form class="form" id="{idp}" data-lead-form novalidate>
<h2>Solicitar atendimento</h2>
<label>Nome<input name="nome" autocomplete="name" required></label>
<label>WhatsApp<input name="whatsapp" type="tel" inputmode="tel" autocomplete="tel" required></label>
<label>Cidade<select name="cidade" required>{cities}</select></label>
<label>Qual tipo de cuidado você precisa?<select name="tipo" required>{opts}</select></label>
<label>Período desejado<select name="periodo"><option>Diurno</option><option>Noturno</option><option>24 horas</option><option>Alguns dias por semana</option><option>A definir</option></select></label>
<label class="check"><input type="checkbox" name="consent" required> Concordo com o uso dos meus dados para contato, conforme a <a href="/politica-de-privacidade/">Política de Privacidade</a> e a <a href="/lgpd/">LGPD</a>.</label>
<button class="btn btn-primary" type="submit">Solicitar atendimento</button>
<p class="note">Ao enviar, abrimos uma conversa no WhatsApp com os dados preenchidos. Nenhum dado é salvo neste site.</p>
</form>'''


def org_schema():
    same = [v for v in C.SOCIAL.values() if v]
    addr = {"@type": "PostalAddress", "streetAddress": C.ADDRESS["street"], "addressLocality": C.ADDRESS["city"],
            "addressRegion": C.ADDRESS["state"], "postalCode": C.ADDRESS["postal"], "addressCountry": C.ADDRESS["country"]}
    o = {"@type": ["Organization", "LocalBusiness"], "@id": f"{C.DOMAIN}/#organization", "name": C.NAME,
         "description": f"Agência de cuidadores que conecta famílias a cuidadores de idosos em {C.CITY} e região.",
         "url": url(""), "logo": f"{C.DOMAIN}/assets/img/favicon.svg", "image": f"{C.DOMAIN}/assets/img/og.jpg",
         "telephone": C.PHONE_E164, "email": C.EMAIL, "address": addr, "taxID": C.CNPJ,
         "areaServed": [{"@type": "City", "name": c["name"]} for c in CITIES],
         "openingHours": C.HOURS, "knowsAbout": ["cuidador de idosos", "cuidado domiciliar", "acompanhamento hospitalar", "cuidados pós-operatórios"]}
    if same:
        o["sameAs"] = same
    return o


def render(path, title, desc, body, crumbs=None, schema=None, kind="website", page_type="page", prio="0.6", noindex=False, article=None):
    """Escreve a página. `schema` = lista de nós extras; WebPage/Breadcrumb são automáticos."""
    crumbs = crumbs or []
    bc_html, bc_schema = breadcrumbs(crumbs) if crumbs else ("", None)
    graph = [{"@type": "WebPage", "@id": url(path) + "#webpage", "url": url(path), "name": title, "description": desc,
              "inLanguage": "pt-BR", "isPartOf": {"@id": f"{C.DOMAIN}/#website"}, "about": {"@id": f"{C.DOMAIN}/#organization"}}]
    if path == "":
        graph += [org_schema(), {"@type": "WebSite", "@id": f"{C.DOMAIN}/#website", "url": url(""), "name": C.NAME,
                                 "inLanguage": "pt-BR", "publisher": {"@id": f"{C.DOMAIN}/#organization"}}]
    else:
        graph.append({"@type": "WebSite", "@id": f"{C.DOMAIN}/#website", "url": url(""), "name": C.NAME})
        if path == "sobre":
            graph.append(org_schema())
    if bc_schema:
        graph.append(bc_schema)
    graph += schema or []
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    canonical = url(path)
    robots = '<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'
    gsc = f'<meta name="google-site-verification" content="{e(C.SEARCH_CONSOLE_TOKEN)}">' if C.SEARCH_CONSOLE_TOKEN else ""
    og_type = "article" if article else "website"
    nav = "".join(f'<a href="{h}">{t}</a>' for t, h in [("Serviços", "/servicos/"), ("Áreas atendidas", "/areas-atendidas/"), ("Blog", "/blog/"),
                                                         ("Sobre", "/sobre/"), ("FAQ", "/faq/"), ("Contato", "/contato/")])
    page = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="pt-BR" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">
{robots}{gsc}
<meta name="theme-color" content="#0f4c5c">
<meta property="og:locale" content="pt_BR"><meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{e(C.NAME)}"><meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="{C.DOMAIN}/assets/img/og.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{C.DOMAIN}/assets/img/og.jpg">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preload" href="/assets/css/style.css" as="style">
<link rel="stylesheet" href="/assets/css/style.css">
<script type="application/ld+json">{ld}</script>
</head>
<body data-page-type="{page_type}" data-page-path="/{path}" data-ga="{e(C.GA4_ID)}">
<a class="skip" href="#main">Pular para o conteúdo</a>
<header class="site-header"><div class="wrap bar">
<a class="brand" href="/" aria-label="{e(C.NAME)} - início">{icon("heart")}<span>{e(C.NAME)}</span></a>
<nav class="nav" aria-label="Principal">{nav}</nav>
{cta_btn("WhatsApp", where="header")}
<details class="menu"><summary aria-label="Abrir menu">Menu</summary><nav class="menu-list" aria-label="Menu mobile">{nav}</nav></details>
</div></header>
<main id="main">
<div class="wrap">{bc_html}</div>
{body}
</main>
<footer class="site-footer"><div class="wrap fgrid">
<div><strong>{e(C.NAME)}</strong><p>Agência de Cuidadores — {e(C.CITY)}/{e(C.REGION)}</p>
<p>CNPJ {e(C.CNPJ)}<br>{e(C.ADDRESS["street"])}, {e(C.ADDRESS["city"])}/{e(C.ADDRESS["state"])}<br>
<a href="tel:{C.PHONE_E164}" data-event="phone_click">{e(C.PHONE)}</a> · <a href="mailto:{e(C.EMAIL)}">{e(C.EMAIL)}</a></p></div>
<div><strong>Serviços</strong><ul>{"".join(f'<li><a href="/{s["slug"]}/">{e(s["name"])}</a></li>' for s in SERVICES)}</ul></div>
<div><strong>Institucional</strong><ul><li><a href="/sobre/">Sobre</a></li><li><a href="/equipe/">Equipe editorial</a></li><li><a href="/qual-agencia-contratar/">Qual agência contratar?</a></li><li><a href="/areas-atendidas/">Áreas atendidas</a></li><li><a href="/blog/">Blog</a></li><li><a href="/faq/">FAQ</a></li><li><a href="/contato/">Contato</a></li></ul></div>
<div><strong>Legal</strong><ul><li><a href="/politica-de-privacidade/">Privacidade</a></li><li><a href="/termos-de-uso/">Termos de uso</a></li><li><a href="/lgpd/">LGPD</a></li><li><a href="/politica-de-cookies/">Cookies</a></li></ul></div>
</div>
<div class="wrap legal-note"><p>O cuidador não é enfermeiro nem médico e não substitui acompanhamento de saúde. © {datetime.date.today().year} {e(C.NAME)}.</p></div></footer>
<div class="mobile-bar"><a class="btn btn-primary" href="{e(wa())}" target="_blank" rel="noopener" data-event="whatsapp_click" data-where="mobile_bar">{icon("wa")}WhatsApp</a>
<a class="btn btn-ghost" href="tel:{C.PHONE_E164}" data-event="phone_click" data-where="mobile_bar">Ligar</a></div>
<div class="consent" id="consent" hidden><p>Usamos cookies de medição para melhorar o site. <a href="/politica-de-cookies/">Saiba mais</a></p>
<button class="btn btn-primary" data-consent="yes">Aceitar</button><button class="btn btn-ghost" data-consent="no">Recusar</button></div>
<script src="/assets/js/app.js" defer></script>
</body></html>'''
    if article:  # não usado; reservado
        pass
    d = OUT / path if path else OUT
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(page, encoding="utf-8")
    if not noindex:
        PAGES.append((path, prio))


def intro_hero(h1, sub, ctas=True, kicker=""):
    k = f'<p class="kicker">{e(kicker)}</p>' if kicker else ""
    c = (f'<div class="actions">{cta_btn("Solicitar um cuidador", where="hero")}'
         f'<a class="btn btn-ghost" href="{e(wa())}" target="_blank" rel="noopener" data-event="whatsapp_click" data-where="hero_secondary">Falar pelo WhatsApp</a></div>') if ctas else ""
    return f'<section class="hero"><div class="wrap">{k}<h1>{h1}</h1><p class="lead">{sub}</p>{c}</div></section>'


def trust_row():
    items = [("shield", "Profissionais selecionados"), ("home", "Atendimento domiciliar"), ("clock", "Escalas diurna, noturna e 24h"), ("users", "Suporte à família")]
    return '<ul class="trust">' + "".join(f"<li>{icon(i)}<span>{t}</span></li>" for i, t in items) + "</ul>"


STEPS = [("Conte a necessidade", "Fale pelo WhatsApp ou formulário: cidade, tipo de cuidado e período."),
         ("Entendemos a rotina", "Conversamos para compreender o perfil do idoso e as expectativas da família."),
         ("Indicamos o profissional", "Apresentamos um cuidador com perfil e experiência compatíveis."),
         ("Combinamos o início", "Definimos horários, tarefas e valores com clareza."),
         ("Acompanhamos", "Acompanhamos o começo do atendimento e ajustamos o que for preciso.")]


def steps_block(title="Como contratar um cuidador em 5 etapas"):
    li = "".join(f"<li><strong>{e(t)}</strong><span>{e(d)}</span></li>" for t, d in STEPS)
    return f'<section class="section"><h2>{title}</h2><ol class="steps">{li}</ol></section>'


def howto_schema(title):
    return {"@type": "HowTo", "name": title, "step": [{"@type": "HowToStep", "position": i + 1, "name": t, "text": d} for i, (t, d) in enumerate(STEPS)]}


def compare_table():
    return ('<table><thead><tr><th>Serviço</th><th>Indicação</th><th>Período</th></tr></thead><tbody>'
            '<tr><td><a href="/cuidador-de-idosos/">Cuidador diário</a></td><td>Rotina</td><td>Dia</td></tr>'
            '<tr><td><a href="/cuidador-noturno/">Cuidador noturno</a></td><td>Acompanhamento</td><td>Noite</td></tr>'
            '<tr><td><a href="/cuidador-24-horas/">Cuidador 24h</a></td><td>Necessidade contínua</td><td>24h</td></tr>'
            '<tr><td><a href="/acompanhante-hospitalar/">Acompanhante hospitalar</a></td><td>Internação e consultas</td><td>Conforme necessidade</td></tr></tbody></table>')


def testimonials():
    if not C.TESTIMONIALS:
        return ""
    q = "".join(f'<blockquote><p>{e(t["text"])}</p><cite>{e(t["author"])}</cite></blockquote>' for t in C.TESTIMONIALS)
    return f'<section class="section"><h2>Depoimentos de famílias</h2><div class="grid">{q}</div></section>'


def facts():
    if not C.FACTS:
        return ""
    return '<ul class="facts">' + "".join(f"<li><strong>{e(a)}</strong><span>{e(b)}</span></li>" for a, b in C.FACTS) + "</ul>"


# ------------------------------------------------------------ páginas
def p_home():
    cards = "".join(f'<a class="card" href="/{s["slug"]}/"><h3>{e(s["name"])}</h3><p>{e(s["short"])}</p></a>' for s in SERVICES)
    cities = "".join(f'<a class="chip" href="/cuidador-de-idosos-em-{c["slug"]}/">Cuidador de idosos em {e(c["name"])}</a>' for c in CITIES)
    body = intro_hero("Cuidadores profissionais para cuidar de quem você ama",
                      "Atendimento domiciliar com profissionais selecionados, acompanhamento personalizado e atendimento conforme a necessidade da sua família.",
                      kicker=f"Agência de cuidadores em {C.CITY} e região") + f'''
<div class="wrap">{trust_row()}{facts()}
{quick_block(f"Somos uma agência de cuidadores que conecta famílias a profissionais para cuidado de idosos e pessoas em recuperação, em casa ou no hospital. Atendemos {C.CITY} e região, com opções diurnas, noturnas e de 24 horas. Para solicitar, basta chamar no WhatsApp.")}
<section class="section"><h2>Sua família precisa de ajuda para cuidar de um idoso?</h2>
<p>Encontramos profissionais preparados para oferecer acompanhamento, companhia e suporte à rotina, de acordo com a necessidade da família.</p>
<div class="actions">{cta_btn("Solicitar um cuidador", where="home_problem")}</div></section>
<section class="section"><h2>Nossos serviços</h2><div class="grid">{cards}</div></section>
<section class="section"><h2>Qual período de cuidado escolher?</h2>{compare_table()}</section>
{steps_block()}
<section class="section"><h2>Por que famílias confiam em nós</h2><div class="grid">
<div class="card"><h3>Seleção criteriosa</h3><p>Indicamos o profissional conforme o perfil da pessoa cuidada e a rotina da casa.</p></div>
<div class="card"><h3>Transparência</h3><p>Tarefas, horários e valores combinados com clareza antes do início.</p></div>
<div class="card"><h3>Suporte à família</h3><p>Canal direto para ajustes e dúvidas durante o atendimento.</p></div>
<div class="card"><h3>Limites claros</h3><p>Cuidador não é enfermeiro nem médico; orientamos quando é preciso um profissional de saúde.</p></div></div></section>
{testimonials()}
<section class="section"><h2>Onde atendemos</h2><p>Cuidadores de idosos em {e(C.CITY)} e região metropolitana.</p><div class="chips">{cities}</div>
<p><a href="/areas-atendidas/">Ver todas as áreas atendidas →</a></p></section>
<section class="section split"><div>{lead_form("home-form")}</div><div><h2>Conteúdo para ajudar sua decisão</h2>
{"".join(f'<p><a href="/blog/{s}/">{e(ART[s]["title"])}</a></p>' for s in ["quanto-custa-um-cuidador-de-idosos", "como-escolher-um-cuidador-de-idosos", "quando-contratar-um-cuidador", "como-escolher-uma-agencia-de-cuidadores"])}</div></section>
{faq_block(GLOBAL_FAQ[:5])}
</div>{cta_band()}'''
    render("", f"Agência de Cuidadores em {C.CITY} | Cuidador de Idosos | {C.NAME}",
           f"Agência de cuidadores em {C.CITY} e região: cuidador de idosos, 24 horas, noturno e acompanhamento hospitalar. Solicite pelo WhatsApp.",
           body, schema=[faq_schema(GLOBAL_FAQ[:5])], page_type="home", prio="1.0")


def p_services_index():
    cards = "".join(f'<a class="card" href="/{s["slug"]}/"><h3>{e(s["name"])}</h3><p>{e(s["short"])}</p></a>' for s in SERVICES)
    crumbs = [("Serviços", "servicos")]
    body = intro_hero("Serviços de cuidadores para cada necessidade", "Escolha o tipo de acompanhamento ou fale conosco para receber orientação.", ctas=False) + f'''
<div class="wrap">{quick_block("Oferecemos cuidador de idosos, cuidador domiciliar, 24 horas, noturno, acompanhante hospitalar, pós-operatório e atendimento para Alzheimer, Parkinson, pessoa acamada e mobilidade reduzida. Todos podem ser contratados em períodos específicos.")}
<section class="section"><h2>Todos os serviços</h2><div class="grid">{cards}</div></section>
<section class="section"><h2>Comparativo de períodos</h2>{compare_table()}</section>
{steps_block()}{faq_block(GLOBAL_FAQ[:4])}</div>{cta_band()}'''
    render("servicos", f"Serviços de Cuidadores de Idosos | {C.NAME}", "Conheça os serviços: cuidador de idosos, 24 horas, noturno, hospitalar, pós-operatório, Alzheimer, Parkinson e mais.",
           body, crumbs, [faq_schema(GLOBAL_FAQ[:4])], prio="0.9")


def p_service(s):
    path = s["slug"]
    crumbs = [("Serviços", "servicos"), (s["name"], path)]
    local = "".join(f'<a class="chip" href="/cuidador-de-idosos-em-{c["slug"]}/">{e(c["name"])}</a>' for c in CITIES)
    schema = [{"@type": "Service", "@id": url(path) + "#service", "name": s["name"], "serviceType": s["name"],
               "description": strip_tags(s["quick"]), "provider": {"@id": f"{C.DOMAIN}/#organization"},
               "areaServed": [{"@type": "City", "name": c["name"]} for c in CITIES], "url": url(path)},
              faq_schema(s["faq"]), howto_schema("Como contratar um cuidador em 5 etapas")]
    body = intro_hero(e(s["h1"]), e(s["short"]), kicker=f"{C.NAME} · {C.CITY}") + f'''
<div class="wrap">{quick_block(s["quick"])}
<section class="section"><h2>{e(s["problem"])}</h2><p>{e(s["solution"])}</p><div class="actions">{cta_btn("Solicitar um cuidador", where="service_problem")}</div></section>
<section class="section"><h2>Para quem é indicado</h2><ul class="list">{"".join(f"<li>{e(i)}</li>" for i in s["who"])}</ul></section>
<section class="section"><h2>Benefícios</h2><div class="grid">{"".join(f'<div class="card">{icon("check")}<p>{e(b)}</p></div>' for b in s["benefits"])}</div></section>
<section class="section"><h2>Como é o atendimento</h2><ul class="list">{"".join(f"<li>{e(i)}</li>" for i in s["features"])}</ul>
<div class="note-box"><strong>O que o cuidador faz e não faz.</strong> {SCOPE_NOTE}</div></section>
{steps_block()}
<section class="section"><h2>Onde oferecemos {e(s["name"].lower())}</h2><div class="chips">{local}</div></section>
{testimonials()}
{faq_block(s["faq"])}
{related_services(s["related"])}
{related_articles(s["blog"], "Guias e artigos sobre o tema")}
</div>{cta_band()}'''
    render(path, f"{s['name']} em {C.CITY} | {C.NAME}", f"{s['name']} em {C.CITY} e região: {s['short']} Solicite pelo WhatsApp.",
           body, crumbs, schema, page_type="service", prio="0.9")


def p_city(c):
    path = f"cuidador-de-idosos-em-{c['slug']}"
    crumbs = [("Áreas atendidas", "areas-atendidas"), (f"Cuidador de idosos em {c['name']}", path)]
    sections = "".join(f"<section class='section'><h2>{e(h)}</h2><p>{e(t)}</p></section>" for h, t in c["local"])
    svc = "".join(f'<li><a href="/{s["slug"]}/">{e(s["name"])} em {e(c["name"])}</a></li>' for s in SERVICES[:6])
    schema = [{"@type": "Service", "name": f"Cuidador de idosos em {c['name']}", "provider": {"@id": f"{C.DOMAIN}/#organization"},
               "areaServed": {"@type": "City", "name": c["name"]}, "serviceType": "Cuidador de idosos", "url": url(path)},
              faq_schema(c["faq"])]
    body = intro_hero(f"Cuidador de idosos em {e(c['name'])}", e(c["intro"]), kicker="Atendimento local") + f'''
<div class="wrap">{quick_block(c["quick"])}{sections}
<section class="section"><h2>Serviços disponíveis em {e(c["name"])}</h2><ul class="list">{svc}</ul></section>
{steps_block()}{faq_block(c["faq"])}
{related_articles(["quanto-custa-um-cuidador-de-idosos", "como-escolher-um-cuidador-de-idosos"])}</div>{cta_band(f"Precisa de um cuidador em {c['name']}?")}'''
    render(path, f"Cuidador de Idosos em {c['name']} | {C.NAME}", f"Cuidador de idosos em {c['name']}: diurno, noturno e 24 horas. {C.NAME}. Solicite pelo WhatsApp.",
           body, crumbs, schema, page_type="local", prio="0.8")


def p_areas():
    cards = "".join(f'<a class="card" href="/cuidador-de-idosos-em-{c["slug"]}/"><h3>{e(c["name"])}</h3><p>Cuidador de idosos em {e(c["name"])}</p></a>' for c in CITIES)
    body = intro_hero("Áreas atendidas", f"Cuidadores de idosos em {e(C.CITY)} e região.", ctas=False) + f'''
<div class="wrap">{quick_block("Atendemos Fortaleza, Caucaia, Eusébio e Aquiraz. Se você mora em outro município da região, consulte pelo WhatsApp: verificamos a disponibilidade de profissionais.")}
<section class="section"><div class="grid">{cards}</div></section>{faq_block(GLOBAL_FAQ[5:6] + GLOBAL_FAQ[:1])}</div>{cta_band()}'''
    render("areas-atendidas", f"Áreas Atendidas | Cuidadores em {C.CITY} e região | {C.NAME}", "Cidades atendidas: Fortaleza, Caucaia, Eusébio e Aquiraz. Consulte disponibilidade pelo WhatsApp.",
           body, [("Áreas atendidas", "areas-atendidas")], [faq_schema(GLOBAL_FAQ[5:6] + GLOBAL_FAQ[:1])], prio="0.8")


def p_blog_index():
    clusters = {}
    for a in ARTICLES:
        clusters.setdefault(a["cluster"], []).append(a)
    cards = "".join(f'<a class="card post" data-title="{e(a["title"].lower())}" href="/blog/{a["slug"]}/"><span class="tag">{e(a["cluster"])}</span><h3>{e(a["title"])}</h3><p>{strip_tags(a["quick"])[:130]}…</p></a>' for a in ARTICLES)
    body = intro_hero("Blog: guias sobre cuidadores e cuidado de idosos", "Respostas diretas para dúvidas de quem cuida e de quem quer contratar.", ctas=False) + f'''
<div class="wrap"><div class="search"><label for="q">Buscar no blog</label><input id="q" type="search" placeholder="Ex.: quanto custa, Alzheimer, quedas" data-blog-search></div>
<div class="grid" id="posts">{cards}</div><p id="none" hidden>Nenhum artigo encontrado.</p>
<section class="section"><h2>Temas</h2><div class="chips">{"".join(f'<span class="chip">{e(k)} ({len(v)})</span>' for k, v in clusters.items())}</div></section></div>{cta_band()}'''
    render("blog", f"Blog: Guias sobre Cuidadores de Idosos | {C.NAME}", "Guias práticos sobre contratar cuidador, custo, rotina, Alzheimer, Parkinson e segurança de idosos.",
           body, [("Blog", "blog")], [{"@type": "CollectionPage", "name": "Blog", "url": url("blog")}], page_type="blog", prio="0.8")


def p_article(a):
    path = f"blog/{a['slug']}"
    secs = "".join(f"<section class='section'><h2>{e(h)}</h2>{t}</section>" for h, t in a["sections"])
    faq = a.get("faq", [])
    same = [x["slug"] for x in ARTICLES if x["cluster"] == a["cluster"] and x["slug"] != a["slug"]][:3]
    more = same + [x["slug"] for x in ARTICLES if x["slug"] not in same and x["slug"] != a["slug"]][: 3 - len(same)]
    svc_links = "".join(f'<a class="btn btn-ghost" href="/{s}/">{e(SVC[s]["name"])}</a>' for s in a["services"])
    schema = [{"@type": "Article", "headline": a["title"], "description": strip_tags(a["quick"]), "inLanguage": "pt-BR",
               "datePublished": TODAY, "dateModified": TODAY, "mainEntityOfPage": url(path),
               "author": {"@type": "Organization", "name": C.NAME, "url": url("equipe")}, "publisher": {"@id": f"{C.DOMAIN}/#organization"},
               "image": f"{C.DOMAIN}/assets/img/og.jpg"}]
    if faq:
        schema.append(faq_schema(faq))
    body = intro_hero(e(a["title"]), f'Por {e(C.NAME)} · atualizado em {TODAY[8:]}/{TODAY[5:7]}/{TODAY[:4]}', ctas=False) + f'''
<div class="wrap article">{quick_block(a["quick"])}{secs}
<div class="note-box"><strong>Importante.</strong> Este conteúdo é informativo e não substitui orientação de médico, enfermeiro ou outro profissional de saúde.</div>
<section class="section"><h2>Precisa de ajuda profissional?</h2><div class="actions">{svc_links}{cta_btn("Solicitar um cuidador", where="article")}</div></section>
{faq_block(faq) if faq else ""}{related_articles(more, "Leia também")}</div>{cta_band()}'''
    render(path, f"{a['title']} | {C.NAME}", strip_tags(a["quick"])[:155] + "…", body,
           [("Blog", "blog"), (a["title"], path)], schema, page_type="article", prio="0.7", article=a)


def simple(path, title, desc, h1, sub, inner, crumbs_label=None, schema=None, prio="0.5", noindex=False, page_type="page"):
    body = intro_hero(h1, sub, ctas=False) + f'<div class="wrap prose">{inner}</div>'
    render(path, title, desc, body, [(crumbs_label or h1, path)], schema, prio=prio, noindex=noindex, page_type=page_type)


def p_about():
    inner = f'''{quick_block(f"{C.NAME} é uma agência de cuidadores com sede em {C.CITY}/{C.REGION}, que conecta famílias a profissionais para cuidado domiciliar e hospitalar de idosos e pessoas em recuperação.")}
<h2>Quem somos</h2><p>{e(C.NAME)} atua na indicação de cuidadores conforme a necessidade de cada família. [Conte aqui a história real da agência: fundação, motivação, experiência da equipe.]</p>
<h2>Dados da empresa</h2><ul class="list"><li>Razão/nome: {e(C.NAME)}</li><li>CNPJ: {e(C.CNPJ)}</li><li>Endereço: {e(C.ADDRESS["street"])}, {e(C.ADDRESS["city"])}/{e(C.ADDRESS["state"])}</li><li>Telefone: {e(C.PHONE)}</li><li>WhatsApp: <a href="{e(wa())}" data-event="whatsapp_click">falar agora</a></li><li>E-mail: {e(C.EMAIL)}</li><li>Funcionamento: {e(C.HOURS)}</li></ul>
<h2>O que oferecemos</h2><p>Veja a lista completa em <a href="/servicos/">Serviços</a>. Atendemos <a href="/areas-atendidas/">Fortaleza, Caucaia, Eusébio e Aquiraz</a>.</p>
<h2>Como selecionamos profissionais</h2><p>[Descreva o processo real: entrevista, verificação de documentos e referências, treinamentos, acompanhamento.]</p>
<h2>Nossos princípios</h2><ul class="list"><li>Transparência sobre o que o cuidador faz e não faz</li><li>Respeito à dignidade e à rotina do idoso</li><li>Suporte à família</li></ul>
<h2>Perfis oficiais</h2><ul class="list">{"".join(f'<li><a rel="me noopener" href="{e(v)}">{e(k)}</a></li>' for k, v in C.SOCIAL.items() if v) or "<li>[Adicione links de Google Business Profile e redes sociais]</li>"}</ul>
<h2>Parcerias e imprensa</h2><p>Profissionais de saúde, clínicas, associações e veículos de comunicação podem falar conosco em <a href="mailto:{e(C.EMAIL)}">{e(C.EMAIL)}</a>.</p>'''
    simple("sobre", f"Sobre a {C.NAME} | Agência de Cuidadores em {C.CITY}", f"Conheça a {C.NAME}: quem somos, dados da empresa, serviços, áreas atendidas e como selecionamos cuidadores.",
           "Sobre a agência", f"Agência de cuidadores em {C.CITY}/{C.REGION}", inner, "Sobre", prio="0.8")


def p_team():
    inner = f'''{quick_block("Nosso conteúdo é produzido pela equipe editorial da agência a partir da experiência prática no atendimento a famílias e revisado antes da publicação. Não substitui orientação de profissionais de saúde.")}
<h2>Como produzimos conteúdo</h2><ul class="list"><li>Foco em respostas diretas e úteis</li><li>Fontes externas citadas quando a afirmação depende delas</li><li>Sem estatísticas inventadas</li><li>Revisão periódica</li></ul>
<h2>Autores e revisores</h2><p>[Liste aqui pessoas reais, cargo, formação e experiência — e só então adicione schema Person com links verificáveis.]</p>'''
    simple("equipe", f"Equipe Editorial | {C.NAME}", "Conheça como produzimos e revisamos o conteúdo do blog.", "Equipe editorial", "Quem escreve e revisa o conteúdo", inner, "Equipe", prio="0.4")


def p_which_agency():
    crit = [("Processo de seleção", "Como o profissional é escolhido e verificado?"), ("Experiência", "Há experiência com o perfil do idoso?"),
            ("Atendimento", "Quem responde a família e em quanto tempo?"), ("Cobertura geográfica", "A agência atende o seu bairro?"),
            ("Suporte à família", "Há acompanhamento após o início?"), ("Disponibilidade", "Há reposição quando o profissional falta?"),
            ("Transparência", "Valores, tarefas e contrato são claros?"), ("Depoimentos reais", "Existem relatos verificáveis de famílias?")]
    rows = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in crit)
    faq = [("Qual agência de cuidadores devo contratar?", "A que for transparente sobre seleção, contrato, valores e reposição, atender sua região e responder com clareza. Use o checklist desta página para comparar."),
           ("Como saber se uma agência é confiável?", "Verifique CNPJ, endereço, contratos claros, referências reais e canais de contato. Desconfie de promessas exageradas.")]
    inner = f'''{quick_block("Não existe agência ideal para todos. A melhor escolha é a que demonstra critérios verificáveis: processo de seleção, transparência de contrato, cobertura na sua região, suporte à família e reposição de profissionais. Compare pelo checklist abaixo.")}
<h2>Checklist para comparar agências</h2><table><thead><tr><th>Critério</th><th>Pergunta a fazer</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Como respondemos a esses critérios</h2><p>[Descreva, com fatos reais, como a {e(C.NAME)} atende cada ponto.]</p>
<h2>Leia também</h2><p><a href="/blog/como-escolher-uma-agencia-de-cuidadores/">Como escolher uma agência de cuidadores?</a> · <a href="/blog/quais-perguntas-fazer-antes-de-contratar-um-cuidador/">Perguntas antes de contratar</a></p>
{faq_block(faq)}'''
    simple("qual-agencia-contratar", f"Qual Agência de Cuidadores Contratar? Checklist | {C.NAME}", "Critérios para escolher uma agência de cuidadores com segurança: seleção, contrato, cobertura e suporte.",
           "Qual agência de cuidadores devo contratar?", "Um checklist objetivo para decidir com segurança", inner, "Qual agência contratar?", [faq_schema(faq)], "0.7")


def p_faq():
    inner = quick_block("Aqui estão as respostas mais comuns sobre contratar cuidador de idosos: atendimento, períodos, seleção, cidades, valores e limites do serviço.") + faq_block(GLOBAL_FAQ, "Perguntas frequentes sobre cuidadores")
    simple("faq", f"Perguntas Frequentes sobre Cuidadores de Idosos | {C.NAME}", "Respostas sobre atendimento domiciliar, cuidador noturno, seleção, valores e cidades atendidas.",
           "Perguntas frequentes", "Respostas diretas para sua decisão", inner, "FAQ", [faq_schema(GLOBAL_FAQ)], "0.7")


def p_contact():
    inner = f'''{quick_block(f"Para solicitar um cuidador, chame no WhatsApp ou preencha o formulário. Atendemos {C.CITY} e região e respondemos com orientação sobre o melhor formato de cuidado.")}
<div class="split"><div>{lead_form("contact-form")}</div><div><h2>Outros canais</h2>
<p>{cta_btn("Solicitar orçamento pelo WhatsApp", where="contact")}</p>
<p>Telefone: <a href="tel:{C.PHONE_E164}" data-event="phone_click">{e(C.PHONE)}</a></p><p>E-mail: <a href="mailto:{e(C.EMAIL)}">{e(C.EMAIL)}</a></p>
<p>{e(C.ADDRESS["street"])}, {e(C.ADDRESS["city"])}/{e(C.ADDRESS["state"])}<br>CNPJ {e(C.CNPJ)}<br>{e(C.HOURS)}</p></div></div>'''
    simple("contato", f"Contato | Solicite um Cuidador | {C.NAME}", f"Fale com a {C.NAME}: WhatsApp, telefone, e-mail e formulário para solicitar cuidador.",
           "Contato", "Fale com um especialista", inner, "Contato", [{"@type": "ContactPage", "url": url("contato")}], "0.8")


def legal(path, title, text):
    simple(path, f"{title} | {C.NAME}", f"{title} da {C.NAME}.", title, f"Última atualização: {TODAY[8:]}/{TODAY[5:7]}/{TODAY[:4]}", text, title, prio="0.2")


def p_legal():
    legal("politica-de-privacidade", "Política de Privacidade",
          f"<p>A {e(C.NAME)} (CNPJ {e(C.CNPJ)}) respeita a sua privacidade. Coletamos apenas os dados que você informa nos formulários (nome, WhatsApp, cidade, tipo de cuidado e período) para entrar em contato e atender à sua solicitação.</p>"
          "<h2>Finalidade e base legal</h2><p>Atendimento da solicitação (execução de procedimentos preliminares a contrato) e, quando aplicável, consentimento.</p>"
          "<h2>Compartilhamento</h2><p>Não vendemos dados. O formulário abre uma conversa no WhatsApp (serviço de terceiro, com política própria).</p>"
          f"<h2>Seus direitos</h2><p>Você pode solicitar acesso, correção ou exclusão pelo e-mail {e(C.EMAIL)}. Veja a página <a href='/lgpd/'>LGPD</a>.</p>"
          "<p><em>[Revise este texto com assessoria jurídica antes de publicar.]</em></p>")
    legal("termos-de-uso", "Termos de Uso",
          f"<p>Ao usar este site você concorda com estes termos. O conteúdo é informativo e não substitui orientação de profissionais de saúde. Os serviços da {e(C.NAME)} são contratados mediante acordo próprio, com valores e condições informados antes do início.</p>"
          "<h2>Limites do serviço</h2><p>O cuidador não é enfermeiro nem médico e não realiza procedimentos de saúde que exigem profissional habilitado.</p>"
          "<p><em>[Revise com assessoria jurídica.]</em></p>")
    legal("lgpd", "LGPD — Lei Geral de Proteção de Dados",
          f"<p>Tratamos dados pessoais conforme a Lei nº 13.709/2018. Controlador: {e(C.NAME)}, CNPJ {e(C.CNPJ)}. Encarregado/contato: {e(C.EMAIL)}.</p>"
          "<h2>Direitos do titular</h2><ul class='list'><li>Confirmação e acesso aos dados</li><li>Correção</li><li>Anonimização, bloqueio ou eliminação</li><li>Portabilidade</li><li>Revogação do consentimento</li></ul>"
          "<h2>Consentimento de formulário</h2><p>Os formulários exigem consentimento expresso, registrado ao marcar a caixa correspondente antes do envio.</p>"
          "<p><em>[Revise com assessoria jurídica.]</em></p>")
    legal("politica-de-cookies", "Política de Cookies",
          "<p>Usamos cookies de medição (Google Analytics) somente após o seu consentimento, para entender quais páginas ajudam mais as famílias. Você pode recusar sem prejuízo ao uso do site.</p>"
          "<p>Para limpar sua escolha, apague os dados do site no navegador.</p><p><em>[Revise com assessoria jurídica.]</em></p>")


def p_404():
    body = intro_hero("Página não encontrada", "O endereço pode ter mudado. Veja nossos serviços ou fale conosco.", ctas=False) + \
        f'<div class="wrap"><div class="actions"><a class="btn btn-primary" href="/">Ir para o início</a><a class="btn btn-ghost" href="/servicos/">Ver serviços</a>{cta_btn("Falar no WhatsApp", where="404", primary=False)}</div></div>'
    render("404-tmp", "Página não encontrada | " + C.NAME, "Página não encontrada.", body, noindex=True)
    (OUT / "404.html").write_text((OUT / "404-tmp" / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
    shutil.rmtree(OUT / "404-tmp")


# ------------------------------------------------------------ arquivos técnicos
def tech_files():
    urls = "".join(f"<url><loc>{url(p)}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>" for p, pr in PAGES)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {C.DOMAIN}/sitemap.xml\n", encoding="utf-8")
    (OUT / "manifest.webmanifest").write_text(json.dumps({"name": C.NAME, "short_name": C.NAME[:12], "start_url": "/", "display": "standalone",
                                                           "background_color": "#fbf7f2", "theme_color": "#0f4c5c", "lang": "pt-BR",
                                                           "icons": [{"src": "/assets/img/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}, ensure_ascii=False), encoding="utf-8")
    svc = "\n".join(f"- [{s['name']}]({url(s['slug'])}): {s['short']}" for s in SERVICES)
    cit = "\n".join(f"- [Cuidador de idosos em {c['name']}]({url('cuidador-de-idosos-em-' + c['slug'])})" for c in CITIES)
    art = "\n".join(f"- [{a['title']}]({url('blog/' + a['slug'])})" for a in ARTICLES)
    llms = f"""# {C.NAME}

> Agência de cuidadores em {C.CITY}/{C.REGION}. Conecta famílias a cuidadores para cuidado domiciliar e hospitalar de idosos e pessoas em recuperação. O cuidador não é enfermeiro nem médico.

Dados: CNPJ {C.CNPJ} · {C.ADDRESS['street']}, {C.ADDRESS['city']}/{C.ADDRESS['state']} · Tel {C.PHONE} · {C.EMAIL} · {C.DOMAIN}

## Serviços
{svc}

## Áreas atendidas
{cit}
- [Todas as áreas]({url('areas-atendidas')})

## Páginas prioritárias
- [Sobre]({url('sobre')})
- [Qual agência contratar?]({url('qual-agencia-contratar')})
- [FAQ]({url('faq')})
- [Contato]({url('contato')})

## Guias
{art}
"""
    (OUT / "llms.txt").write_text(llms, encoding="utf-8")
    (OUT / "_redirects").write_text("# Netlify/Cloudflare Pages\nhttp://www.exemplo.com.br/* https://www.exemplo.com.br/:splat 301!\n"
                                    "/cuidadores /servicos/ 301\n/cuidador /cuidador-de-idosos/ 301\n/cuidador-de-idosos-fortaleza /cuidador-de-idosos-em-fortaleza/ 301\n"
                                    "/acompanhante-de-idosos /cuidador-de-idosos/ 301\n/cuidador-noite /cuidador-noturno/ 301\n/cuidador-24h /cuidador-24-horas/ 301\n"
                                    "/*  /404.html 404\n", encoding="utf-8")
    (OUT / ".htaccess").write_text("""# Apache
ErrorDocument 404 /404.html
RewriteEngine On
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} !^www\\. [NC]
RewriteRule ^ https://www.exemplo.com.br%{REQUEST_URI} [L,R=301]
Redirect 301 /cuidadores /servicos/
Redirect 301 /cuidador-24h /cuidador-24-horas/
Redirect 301 /cuidador-noite /cuidador-noturno/
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType text/css "access plus 1 year"
ExpiresByType application/javascript "access plus 1 year"
ExpiresByType image/svg+xml "access plus 1 year"
</IfModule>
""", encoding="utf-8")


def warn():
    miss = [k for k, v in {"NAME": C.NAME, "CITY": C.CITY, "REGION": C.REGION, "CNPJ": C.CNPJ, "ADDRESS": C.ADDRESS["street"]}.items() if "[" in str(v)]
    if "exemplo" in C.DOMAIN:
        miss.append("DOMAIN")
    if C.WHATSAPP.endswith("0000000"):
        miss.append("WHATSAPP")
    if miss:
        print("ATENCAO - preencha em config.py:", ", ".join(miss))
    print("Revise textos marcados com [ ... ] nas páginas Sobre, Equipe, Qual agência e legais.")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    p_home(); p_services_index()
    for s in SERVICES: p_service(s)
    for c in CITIES: p_city(c)
    p_areas(); p_blog_index()
    for a in ARTICLES: p_article(a)
    p_about(); p_team(); p_which_agency(); p_faq(); p_contact(); p_legal(); p_404()
    tech_files(); warn()
    print(f"OK: {len(PAGES)} páginas em {OUT}")


if __name__ == "__main__":
    main()
