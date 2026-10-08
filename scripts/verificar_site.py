#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from PIL import Image
import xml.etree.ElementTree as ET
import tinycss2
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
warnings = []


def local_target(current: Path, ref: str):
    if not ref or ref.startswith(('#', 'mailto:', 'tel:', 'data:', 'javascript:')):
        return None
    parsed = urlparse(ref)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    if path.startswith('/'):
        target = ROOT / path.lstrip('/')
    else:
        target = current.parent / path
    if path.endswith('/'):
        target = target / 'index.html'
    return target.resolve()

html_files = sorted(ROOT.rglob('*.html'))
for html in html_files:
    text = html.read_text(encoding='utf-8')
    soup = BeautifulSoup(text, 'html.parser')
    rel = html.relative_to(ROOT)

    # Basic document checks
    if not text.lstrip().lower().startswith('<!doctype html>'):
        errors.append(f'{rel}: <!doctype html> ausente ou incorreto')
    if not soup.html or soup.html.get('lang') != 'pt-BR':
        errors.append(f'{rel}: html lang="pt-BR" ausente')
    if not soup.title or not soup.title.get_text(strip=True):
        errors.append(f'{rel}: <title> ausente')
    if not soup.find('meta', attrs={'name': 'viewport'}):
        errors.append(f'{rel}: meta viewport ausente')

    # Duplicate IDs
    ids = [tag.get('id') for tag in soup.find_all(attrs={'id': True})]
    dup = sorted({x for x in ids if ids.count(x) > 1})
    if dup:
        errors.append(f'{rel}: IDs duplicados: {dup}')

    # Accidental Markdown in URL attributes
    for tag in soup.find_all(True):
        for attr in ('href', 'src', 'srcset'):
            val = tag.get(attr)
            if isinstance(val, str) and re.search(r'\[[^\]]+\]\([^\)]+\)', val):
                errors.append(f'{rel}: sintaxe Markdown em {attr}: {val}')

    # Links, styles, images, sources
    for tag, attr in [('a','href'), ('link','href'), ('img','src'), ('source','srcset')]:
        for node in soup.find_all(tag):
            val = node.get(attr)
            if not val:
                if tag in ('img','source','link'):
                    errors.append(f'{rel}: <{tag}> sem {attr}')
                continue
            target = local_target(html, val.split()[0])
            if target and not target.exists():
                errors.append(f'{rel}: referência local quebrada: {val}')

    # Images: alt and intrinsic dimensions
    for img in soup.find_all('img'):
        if not img.has_attr('alt'):
            errors.append(f'{rel}: imagem sem alt: {img.get("src")}')
        src = img.get('src')
        target = local_target(html, src) if src else None
        if target and target.exists() and target.suffix.lower() in {'.png','.jpg','.jpeg','.webp'}:
            try:
                with Image.open(target) as im:
                    w, h = im.size
                aw, ah = img.get('width'), img.get('height')
                if aw and ah:
                    try:
                        if (int(aw), int(ah)) != (w, h):
                            errors.append(f'{rel}: dimensões HTML {aw}x{ah} != arquivo {w}x{h}: {src}')
                    except ValueError:
                        errors.append(f'{rel}: width/height inválidos em {src}')
            except Exception as e:
                errors.append(f'{rel}: erro lendo imagem {src}: {e}')

    # External links opened in new tab must be safe; project policy says all external links new tab.
    for a in soup.find_all('a', href=True):
        href = a['href']
        parsed = urlparse(href)
        if parsed.scheme in ('http','https'):
            if a.get('target') != '_blank':
                errors.append(f'{rel}: link externo sem target="_blank": {href}')
            relvals = a.get('rel') or []
            if not {'noopener','noreferrer'}.issubset(set(relvals)):
                errors.append(f'{rel}: link externo sem rel="noopener noreferrer": {href}')

# CSS parsing
for css in sorted(ROOT.rglob('*.css')):
    text = css.read_text(encoding='utf-8')
    rules = tinycss2.parse_stylesheet(text, skip_comments=False, skip_whitespace=False)
    for rule in rules:
        if rule.type == 'error':
            errors.append(f'{css.relative_to(ROOT)}: erro CSS: {rule.message}')

# RSS parsing
feed = ROOT / 'feed.xml'
try:
    tree = ET.parse(feed)
    root_el = tree.getroot()
    if root_el.tag != 'rss':
        errors.append('feed.xml: elemento raiz não é <rss>')
    items = root_el.findall('./channel/item')
    if not items:
        errors.append('feed.xml: nenhum <item> publicado')
except Exception as e:
    errors.append(f'feed.xml: XML inválido: {e}')

# Sitemap parsing
sitemap = ROOT / 'sitemap.xml'
try:
    ET.parse(sitemap)
except Exception as e:
    errors.append(f'sitemap.xml: XML inválido: {e}')

robots = ROOT / 'robots.txt'
if not robots.exists() or 'Sitemap: https://alexbonnamain.github.io/sitemap.xml' not in robots.read_text(encoding='utf-8'):
    errors.append('robots.txt: referência ao sitemap ausente')

# Specific publication assets
for required in [
    ROOT/'assets/images/site/favicon.svg',
    ROOT/'assets/images/softwares/logos/librewolf.svg',
    ROOT/'artigos/seu-computador-ainda-e-seu-01/01.webp',
]:
    if not required.exists():
        errors.append(f'arquivo obrigatório ausente: {required.relative_to(ROOT)}')

if errors:
    print('ERROS ENCONTRADOS:')
    for e in errors:
        print('-', e)
    if warnings:
        print('\nAVISOS:')
        for w in warnings:
            print('-', w)
    sys.exit(1)

print('OK — verificações locais concluídas sem erros.')
if warnings:
    print('\nAVISOS:')
    for w in warnings:
        print('-', w)
