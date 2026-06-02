"""
Document enhancers for Markdown processing
"""

import re
from typing import Dict, Any, List
from .core import Document, Block, BlockType


class TOCEnhancer:
    """Add table of contents to document"""

    def __init__(self, max_depth: int = 6, min_depth: int = 1):
        self.max_depth = max_depth
        self.min_depth = min_depth

    def __call__(self, doc: Document) -> Document:
        if not doc.toc:
            return doc

        # Filter TOC by depth
        filtered_toc = [
            item for item in doc.toc
            if self.min_depth <= item['level'] <= self.max_depth
        ]

        # Generate TOC HTML
        toc_html = self._generate_toc_html(filtered_toc)

        # Add TOC block at the beginning
        toc_block = Block(
            type=BlockType.RAW_HTML,
            content=toc_html,
            metadata={'is_toc': True}
        )

        doc.blocks.insert(0, toc_block)
        return doc

    def _generate_toc_html(self, toc: List[Dict[str, Any]]) -> str:
        """Generate TOC HTML"""
        if not toc:
            return ''

        html = ['<nav class="toc">']
        html.append('<h2>Table of Contents</h2>')
        html.append('<ul>')

        current_level = toc[0]['level']
        stack = [current_level]

        for item in toc:
            level = item['level']

            if level > current_level:
                html.append('<ul>')
                stack.append(level)
            elif level < current_level:
                while stack and stack[-1] > level:
                    html.append('</ul>')
                    stack.pop()

            html.append(
                f'<li><a href="#{item["anchor"]}">{item["title"]}</a></li>'
            )
            current_level = level

        while stack:
            html.append('</ul>')
            stack.pop()

        html.append('</nav>')
        return '\n'.join(html)


class CodeHighlightEnhancer:
    """Enhance code blocks with syntax highlighting"""

    # Simple syntax highlighting patterns
    KEYWORDS = [
        'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'return',
        'import', 'from', 'as', 'try', 'except', 'finally', 'with',
        'lambda', 'yield', 'async', 'await', 'pass', 'break', 'continue',
        'function', 'var', 'let', 'const', 'return', 'if', 'else',
        'for', 'while', 'class', 'extends', 'super', 'new', 'this'
    ]

    BUILTINS = [
        'print', 'len', 'range', 'enumerate', 'zip', 'map', 'filter',
        'open', 'input', 'int', 'str', 'float', 'list', 'dict', 'set',
        'True', 'False', 'None', 'console', 'document', 'window',
        'Math', 'JSON', 'Array', 'Object', 'String'
    ]

    def __init__(self, theme: str = 'default'):
        self.theme = theme

    def __call__(self, doc: Document) -> Document:
        for block in doc.blocks:
            if block.type == BlockType.CODE_BLOCK:
                block.content = self._highlight(
                    block.content,
                    block.metadata.get('language', 'text')
                )
                block.metadata['highlighted'] = True
        return doc

    def _highlight(self, code: str, language: str) -> str:
        """Apply syntax highlighting"""
        lines = code.split('\n')
        highlighted_lines = []

        for line in lines:
            highlighted = self._highlight_line(line, language)
            highlighted_lines.append(highlighted)

        return '\n'.join(highlighted_lines)

    def _highlight_line(self, line: str, language: str) -> str:
        """Highlight a single line"""
        # Comments
        if language in ['python', 'py']:
            comment_match = re.match(r'^(.*?)(#.*)$', line)
            if comment_match:
                code_part = self._highlight_code_part(comment_match.group(1), language)
                comment_part = f'<span class="comment">{html.escape(comment_match.group(2))}</span>'
                return code_part + comment_part

        # String literals
        line = self._highlight_strings(line)

        # Keywords
        for keyword in self.KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            line = re.sub(
                pattern,
                f'<span class="keyword">{keyword}</span>',
                line
            )

        # Builtins
        for builtin in self.BUILTINS:
            pattern = r'\b' + re.escape(builtin) + r'\b'
            line = re.sub(
                pattern,
                f'<span class="builtin">{builtin}</span>',
                line
            )

        # Numbers
        line = re.sub(
            r'\b(\d+(?:\.\d+)?)\b',
            r'<span class="number">\1</span>',
            line
        )

        return line

    def _highlight_strings(self, line: str) -> str:
        """Highlight string literals"""
        # Double quotes
        line = re.sub(
            r'"([^"\\]|\\.)*"',
            lambda m: f'<span class="string">{html.escape(m.group(0))}</span>',
            line
        )
        # Single quotes
        line = re.sub(
            r"'([^'\\]|\\.)*'",
            lambda m: f'<span class="string">{html.escape(m.group(0))}</span>',
            line
        )
        return line

    def _highlight_code_part(self, code: str, language: str) -> str:
        """Highlight code part (without comments)"""
        return self._highlight_line(code, language)


class MathEnhancer:
    """Enhance math blocks with LaTeX rendering support"""

    def __init__(self, renderer: str = 'katex'):
        self.renderer = renderer

    def __call__(self, doc: Document) -> Document:
        for block in doc.blocks:
            if block.type == BlockType.MATH_BLOCK:
                block.metadata['renderer'] = self.renderer
                block.metadata['math_html'] = self._wrap_math(block.content)
        return doc

    def _wrap_math(self, math: str) -> str:
        """Wrap math content for rendering"""
        if self.renderer == 'katex':
            return f'<div class="math-block" data-katex="{html.escape(math)}">\\[{math}\\]</div>'
        elif self.renderer == 'mathjax':
            return f'<div class="math-block">\\[{math}\\]</div>'
        else:
            return f'<pre class="math">{html.escape(math)}</pre>'


class LinkEnhancer:
    """Enhance links with additional attributes"""

    def __init__(self, external_new_tab: bool = True, add_nofollow: bool = False):
        self.external_new_tab = external_new_tab
        self.add_nofollow = add_nofollow

    def __call__(self, doc: Document) -> Document:
        # This enhancer works at render time
        doc.metadata['link_enhancer'] = {
            'external_new_tab': self.external_new_tab,
            'add_nofollow': self.add_nofollow
        }
        return doc


class ImageEnhancer:
    """Enhance images with lazy loading and captions"""

    def __init__(self, lazy_load: bool = True, responsive: bool = True):
        self.lazy_load = lazy_load
        self.responsive = responsive

    def __call__(self, doc: Document) -> Document:
        doc.metadata['image_enhancer'] = {
            'lazy_load': self.lazy_load,
            'responsive': self.responsive
        }
        return doc


class AnchorEnhancer:
    """Add anchors to headings"""

    def __call__(self, doc: Document) -> Document:
        for block in doc.blocks:
            if block.type == BlockType.HEADING:
                anchor = self._slugify(block.content)
                block.metadata['anchor'] = anchor
        return doc

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')


# Import html for escape
import html
