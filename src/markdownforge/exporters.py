"""
Document exporters for various formats
"""

import os
import re
import html
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .core import Document, Block, BlockType


class BaseExporter(ABC):
    """Base class for document exporters"""

    def __init__(self, theme: str = 'default'):
        self.theme = theme

    @abstractmethod
    def export(self, doc: Document, output_path: Optional[str] = None) -> str:
        """Export document to the target format"""
        pass

    def _get_default_template(self) -> str:
        """Get default HTML template"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css}</style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>'''


class HTMLExporter(BaseExporter):
    """Export document to HTML"""

    def __init__(self, theme: str = 'default', standalone: bool = True):
        super().__init__(theme)
        self.standalone = standalone

    def export(self, doc: Document, output_path: Optional[str] = None) -> str:
        """Export document to HTML"""
        content = self._render_document(doc)

        if self.standalone:
            css = self._get_css()
            title = doc.metadata.get('title', 'Untitled Document')
            html_output = self._get_default_template().format(
                title=html.escape(title),
                css=css,
                content=content
            )
        else:
            html_output = content

        if output_path:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_output)

        return html_output

    def _render_document(self, doc: Document) -> str:
        """Render document blocks to HTML"""
        parts = []

        for block in doc.blocks:
            html_part = self._render_block(block)
            if html_part:
                parts.append(html_part)

        return '\n'.join(parts)

    def _render_block(self, block: Block) -> str:
        """Render a single block to HTML"""
        if block.type == BlockType.HEADING:
            level = block.metadata.get('level', 1)
            anchor = block.metadata.get('anchor', '')
            anchor_attr = f' id="{anchor}"' if anchor else ''
            content = self._render_inline(block.content)
            return f'<h{level}{anchor_attr}>{content}</h{level}>'

        elif block.type == BlockType.PARAGRAPH:
            content = self._render_inline(block.content)
            return f'<p>{content}</p>'

        elif block.type == BlockType.CODE_BLOCK:
            language = block.metadata.get('language', 'text')
            code = block.content

            if block.metadata.get('highlighted'):
                # Already highlighted
                code_html = code
            else:
                code_html = html.escape(code)

            return (
                f'<pre><code class="language-{language}">'
                f'{code_html}'
                f'</code></pre>'
            )

        elif block.type == BlockType.MATH_BLOCK:
            if 'math_html' in block.metadata:
                return block.metadata['math_html']
            return f'<pre class="math">{html.escape(block.content)}</pre>'

        elif block.type == BlockType.LIST:
            list_type = block.metadata.get('type', 'unordered')
            items = block.metadata.get('items', [])

            tag = 'ul' if list_type == 'unordered' else 'ol'
            items_html = '\n'.join(
                f'<li>{self._render_inline(item)}</li>' for item in items
            )
            return f'<{tag}>\n{items_html}\n</{tag}>'

        elif block.type == BlockType.QUOTE:
            content = self._render_inline(block.content)
            return f'<blockquote>\n<p>{content}</p>\n</blockquote>'

        elif block.type == BlockType.TABLE:
            headers = block.metadata.get('headers', [])
            rows = block.metadata.get('rows', [])

            thead = '<tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr>'
            tbody = '\n'.join(
                '<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>'
                for row in rows
            )

            return (
                f'<table>\n'
                f'<thead>\n{thead}\n</thead>\n'
                f'<tbody>\n{tbody}\n</tbody>\n'
                f'</table>'
            )

        elif block.type == BlockType.HORIZONTAL_RULE:
            return '<hr>'

        elif block.type == BlockType.RAW_HTML:
            return block.content

        return ''

    def _render_inline(self, text: str) -> str:
        """Render inline markdown elements"""
        # Code span
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

        # Bold
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)

        # Italic
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)

        # Strikethrough
        text = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', text)

        # Links
        text = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2">\1</a>',
            text
        )

        # Images
        text = re.sub(
            r'!\[([^\]]*)\]\(([^)]+)\)',
            r'<img src="\2" alt="\1">',
            text
        )

        # Line breaks
        text = text.replace('  \n', '<br>\n')

        return text

    def _get_css(self) -> str:
        """Get CSS styles"""
        return '''
:root {
    --primary-color: #2563eb;
    --text-color: #1f2937;
    --bg-color: #ffffff;
    --code-bg: #f3f4f6;
    --border-color: #e5e7eb;
    --toc-bg: #f9fafb;
}

* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background: var(--bg-color);
    margin: 0;
    padding: 0;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
}

h1, h2, h3, h4, h5, h6 {
    margin-top: 2rem;
    margin-bottom: 1rem;
    font-weight: 600;
    line-height: 1.25;
}

h1 { font-size: 2.25rem; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem; }
h2 { font-size: 1.75rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.3rem; }
h3 { font-size: 1.5rem; }
h4 { font-size: 1.25rem; }
h5 { font-size: 1.1rem; }
h6 { font-size: 1rem; }

p {
    margin: 0 0 1rem 0;
}

a {
    color: var(--primary-color);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

code {
    background: var(--code-bg);
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
    font-size: 0.9em;
}

pre {
    background: var(--code-bg);
    padding: 1rem;
    border-radius: 6px;
    overflow-x: auto;
    margin: 1rem 0;
}

pre code {
    background: none;
    padding: 0;
}

/* Syntax highlighting */
.keyword { color: #d73a49; font-weight: bold; }
.string { color: #032f62; }
.number { color: #005cc5; }
.comment { color: #6a737d; font-style: italic; }
.builtin { color: #6f42c1; }

blockquote {
    border-left: 4px solid var(--primary-color);
    margin: 1rem 0;
    padding: 0.5rem 1rem;
    background: var(--toc-bg);
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}

th, td {
    border: 1px solid var(--border-color);
    padding: 0.75rem;
    text-align: left;
}

th {
    background: var(--toc-bg);
    font-weight: 600;
}

ul, ol {
    margin: 1rem 0;
    padding-left: 2rem;
}

li {
    margin: 0.25rem 0;
}

hr {
    border: none;
    border-top: 2px solid var(--border-color);
    margin: 2rem 0;
}

/* Table of Contents */
.toc {
    background: var(--toc-bg);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 1.5rem;
    margin: 1rem 0 2rem 0;
}

.toc h2 {
    margin-top: 0;
    font-size: 1.25rem;
}

.toc ul {
    list-style: none;
    padding-left: 0;
    margin: 0;
}

.toc ul ul {
    padding-left: 1.5rem;
}

.toc li {
    margin: 0.5rem 0;
}

.toc a {
    color: var(--text-color);
}

.toc a:hover {
    color: var(--primary-color);
}

/* Math blocks */
.math-block {
    overflow-x: auto;
    margin: 1rem 0;
}

img {
    max-width: 100%;
    height: auto;
}

@media print {
    .toc { display: none; }
    body { font-size: 12pt; }
    pre { white-space: pre-wrap; word-wrap: break-word; }
}
'''


class PDFExporter(BaseExporter):
    """Export document to PDF (via HTML + browser printing)"""

    def export(self, doc: Document, output_path: Optional[str] = None) -> str:
        """Export document to PDF-ready HTML"""
        html_exporter = HTMLExporter(theme=self.theme, standalone=True)
        html_content = html_exporter.export(doc)

        # Add PDF-specific styles
        pdf_css = '''
        @page {
            size: A4;
            margin: 2cm;
        }
        '''

        html_content = html_content.replace(
            '<style>',
            f'<style>{pdf_css}'
        )

        if output_path:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

        return html_content


class WordExporter(BaseExporter):
    """Export document to Word-compatible HTML"""

    def export(self, doc: Document, output_path: Optional[str] = None) -> str:
        """Export document to Word-compatible HTML"""
        content = self._render_document(doc)

        title = doc.metadata.get('title', 'Untitled Document')

        html_output = f'''<!DOCTYPE html>
<html xmlns:o="urn:schemas-microsoft-com:office:office"
      xmlns:w="urn:schemas-microsoft-com:office:word"
      xmlns="http://www.w3.org/TR/REC-html40">
<head>
    <meta charset="utf-8">
    <title>{html.escape(title)}</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; font-size: 12pt; }}
        h1 {{ font-size: 16pt; font-weight: bold; }}
        h2 {{ font-size: 14pt; font-weight: bold; }}
        h3 {{ font-size: 12pt; font-weight: bold; }}
        code {{ font-family: 'Courier New', monospace; background: #f0f0f0; }}
        pre {{ background: #f0f0f0; padding: 10px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ccc; padding: 5px; }}
    </style>
</head>
<body>
    {content}
</body>
</html>'''

        if output_path:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_output)

        return html_output

    def _render_document(self, doc: Document) -> str:
        """Render document blocks to Word HTML"""
        parts = []

        for block in doc.blocks:
            html_part = self._render_block(block)
            if html_part:
                parts.append(html_part)

        return '\n'.join(parts)

    def _render_block(self, block: Block) -> str:
        """Render a single block to Word HTML"""
        if block.type == BlockType.HEADING:
            level = block.metadata.get('level', 1)
            content = self._render_inline(block.content)
            return f'<h{level}>{content}</h{level}>'

        elif block.type == BlockType.PARAGRAPH:
            content = self._render_inline(block.content)
            return f'<p>{content}</p>'

        elif block.type == BlockType.CODE_BLOCK:
            code = html.escape(block.content)
            return f'<pre>{code}</pre>'

        elif block.type == BlockType.LIST:
            list_type = block.metadata.get('type', 'unordered')
            items = block.metadata.get('items', [])

            tag = 'ul' if list_type == 'unordered' else 'ol'
            items_html = '\n'.join(
                f'<li>{self._render_inline(item)}</li>' for item in items
            )
            return f'<{tag}>\n{items_html}\n</{tag}>'

        elif block.type == BlockType.QUOTE:
            content = self._render_inline(block.content)
            return f'<blockquote>\n<p>{content}</p>\n</blockquote>'

        elif block.type == BlockType.TABLE:
            headers = block.metadata.get('headers', [])
            rows = block.metadata.get('rows', [])

            thead = '<tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr>'
            tbody = '\n'.join(
                '<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>'
                for row in rows
            )

            return f'<table>\n{thead}\n{tbody}\n</table>'

        elif block.type == BlockType.HORIZONTAL_RULE:
            return '<hr>'

        return ''

    def _render_inline(self, text: str) -> str:
        """Render inline markdown elements"""
        # Code span
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

        # Bold
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)

        # Italic
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)

        # Links
        text = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2">\1</a>',
            text
        )

        return text
