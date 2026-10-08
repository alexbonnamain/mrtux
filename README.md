# Mr Tux_

**Tecnologia, IA, cibercultura, filosofia e outras inquietações.**

O Mr Tux é um site estático feito à mão com HTML e CSS.

Sem CMS, sem framework, sem build e sem JavaScript.

## URL de publicação

Este pacote está preparado para:

```text
https://alexbonnamain.github.io/
```

Os caminhos iniciados por `/` assumem que o conteúdo deste diretório será publicado na raiz desse GitHub Pages.

## Rodando localmente

```bash
python3 scripts/verificar_site.py
bash scripts/servir-local.sh
```

Depois abra:

```text
http://127.0.0.1:8000/
```

## Estrutura principal

```text
.
├── index.html
├── 404.html
├── feed.xml
├── robots.txt
├── sitemap.xml
├── artigos/
├── softwares/
├── sobre/
├── contato/
├── assets/
│   ├── css/
│   └── images/
└── scripts/
```

## Decisões atuais

- Verde principal: `#00d455`
- Sem fontes externas
- Sem analytics
- Sem CDN
- Cursor piscando apenas no cabeçalho
- Underscore estático no rodapé
- Links externos abrem em nova aba com `rel="noopener noreferrer"`
- RSS em `/feed.xml`
- `.nojekyll` incluído para publicação estática direta no GitHub Pages

## Artigo 01

```text
/artigos/seu-computador-ainda-e-seu-01/seu-computador-ainda-e-seu-01.html
```

A capa usa WebP com PNG de fallback. A imagem interna do Toshiba mantém as dimensões intrínsecas `800 × 599`, mas a apresentação visual é limitada a 500 px no desktop e reduzida responsivamente em telas menores.
