"""
Core Markdown processing engine
"""

import re
import html
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class BlockType(Enum):
    """Markdown block types"""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    LIST = "list"
    QUOTE = "quote"
    TABLE = "table"
    HORIZONTAL_RULE = "horizontal_rule"
    RAW_HTML = "raw_html"
    MATH_BLOCK = "math_block"


@dataclass
class Block:
    """Represents a markdown block element"""
    type: BlockType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List['Block'] = field(default_factory=list)


@dataclass
class Document:
    """Represents a parsed markdown document"""
    blocks: List[Block] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    toc: List[Dict[str, Any]] = field(default_factory=list)


class MarkdownProcessor:
    """
    Core Markdown processor with extensible architecture
    """

    def __init__(self):
        self.enhancers: List[Callable[[Document], Document]] = []
        self._init_parsers()

    def _init_parsers(self):
        """Initialize block parsers"""
        self.parsers = [
            self._parse_code_block,
            self._parse_math_block,
            self._parse_heading,
            self._parse_horizontal_rule,
            self._parse_table,
            self._parse_list,
            self._parse_quote,
            self._parse_raw_html,
            self._parse_paragraph,
        ]

    def add_enhancer(self, enhancer: Callable[[Document], Document]):
        """Add an enhancer to the processing pipeline"""
        self.enhancers.append(enhancer)
        return self

    def parse(self, text: str) -> Document:
        """Parse markdown text into a Document"""
        # Extract YAML frontmatter
        metadata = {}
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
        if frontmatter_match:
            metadata = self._parse_yaml(frontmatter_match.group(1))
            text = text[frontmatter_match.end():]

        # Split into blocks
        blocks = self._split_blocks(text)

        # Parse each block
        parsed_blocks = []
        for block_text in blocks:
            block_text = block_text.strip()
            if not block_text:
                continue

            for parser in self.parsers:
                block = parser(block_text)
                if block:
                    parsed_blocks.append(block)
                    break

        doc = Document(blocks=parsed_blocks, metadata=metadata)

        # Build TOC
        doc.toc = self._build_toc(parsed_blocks)

        return doc

    def process(self, text: str) -> Document:
        """Parse and enhance markdown text"""
        doc = self.parse(text)

        # Apply enhancers
        for enhancer in self.enhancers:
            doc = enhancer(doc)

        return doc

    def _split_blocks(self, text: str) -> List[str]:
        """Split markdown text into blocks"""
        # Handle code blocks specially
        blocks = []
        current_block = []
        in_code_block = False
        code_fence = None

        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Check for code block start/end
            code_match = re.match(r'^(```+|~~~+)', line)
            if code_match:
                fence = code_match.group(1)
                if not in_code_block:
                    # Start of code block
                    if current_block:
                        blocks.append('\n'.join(current_block))
                        current_block = []
                    in_code_block = True
                    code_fence = fence
                    current_block.append(line)
                elif fence.startswith(code_fence[0]) and len(fence) >= len(code_fence):
                    # End of code block
                    current_block.append(line)
                    blocks.append('\n'.join(current_block))
                    current_block = []
                    in_code_block = False
                    code_fence = None
                else:
                    current_block.append(line)
            elif in_code_block:
                current_block.append(line)
            elif stripped == '':
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
            elif re.match(r'^#{1,6}\s+', stripped):
                # ATX heading - start new block
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                current_block.append(line)
                blocks.append('\n'.join(current_block))
                current_block = []
            elif re.match(r'^[=-]+\s*$', stripped):
                # Setext heading underline
                if current_block:
                    current_block.append(line)
                    blocks.append('\n'.join(current_block))
                    current_block = []
                else:
                    # Orphan underline, treat as paragraph
                    current_block.append(line)
            elif re.match(r'^\s*[-*+]\s+', stripped):
                # List item - start new block
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                current_block.append(line)
            elif re.match(r'^\s*\d+\.\s+', stripped):
                # Ordered list item - start new block
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                current_block.append(line)
            elif stripped.startswith('>'):
                # Blockquote - start new block
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                current_block.append(line)
            elif re.match(r'^(---|___|\*\*\*)\s*$', stripped):
                # Horizontal rule
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                blocks.append(line)
            elif stripped.startswith('|'):
                # Table row
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                current_block.append(line)
            else:
                current_block.append(line)
            i += 1

        if current_block:
            blocks.append('\n'.join(current_block))

        return blocks

    def _parse_heading(self, text: str) -> Optional[Block]:
        """Parse heading block"""
        match = re.match(r'^(#{1,6})\s+(.+)$', text)
        if match:
            level = len(match.group(1))
            content = match.group(2).strip()
            return Block(
                type=BlockType.HEADING,
                content=content,
                metadata={'level': level}
            )
        return None

    def _parse_code_block(self, text: str) -> Optional[Block]:
        """Parse code block"""
        match = re.match(r'^(```+|~~~+)(\w*)\s*\n(.*?)\n\1$', text, re.DOTALL)
        if match:
            language = match.group(2) or 'text'
            code = match.group(3)
            return Block(
                type=BlockType.CODE_BLOCK,
                content=code,
                metadata={'language': language}
            )
        return None

    def _parse_math_block(self, text: str) -> Optional[Block]:
        """Parse math block (LaTeX)"""
        if text.startswith('$$') and text.endswith('$$'):
            math = text[2:-2].strip()
            return Block(
                type=BlockType.MATH_BLOCK,
                content=math
            )
        return None

    def _parse_horizontal_rule(self, text: str) -> Optional[Block]:
        """Parse horizontal rule"""
        if re.match(r'^(---|___|\*\*\*)\s*$', text.strip()):
            return Block(
                type=BlockType.HORIZONTAL_RULE,
                content=''
            )
        return None

    def _parse_table(self, text: str) -> Optional[Block]:
        """Parse table block"""
        lines = text.strip().split('\n')
        if len(lines) < 2:
            return None

        # Check for separator line
        separator_pattern = r'^[\s|:|-]+$'
        if not re.match(separator_pattern, lines[1]):
            return None

        # Parse header
        headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
        if not headers:
            return None

        # Parse rows
        rows = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                rows.append(cells)

        return Block(
            type=BlockType.TABLE,
            content=text,
            metadata={'headers': headers, 'rows': rows}
        )

    def _parse_list(self, text: str) -> Optional[Block]:
        """Parse list block"""
        lines = text.split('\n')
        if not lines:
            return None

        # Check if first line is a list item
        first_line = lines[0]
        unordered_match = re.match(r'^(\s*)[-*+]\s+(.+)$', first_line)
        ordered_match = re.match(r'^(\s*)\d+\.\s+(.+)$', first_line)

        if not unordered_match and not ordered_match:
            return None

        list_type = 'unordered' if unordered_match else 'ordered'

        # Parse list items
        items = []
        current_item = []
        base_indent = len(unordered_match.group(1)) if unordered_match else len(ordered_match.group(1))

        for line in lines:
            unordered = re.match(r'^(\s*)[-*+]\s+(.+)$', line)
            ordered = re.match(r'^(\s*)\d+\.\s+(.+)$', line)

            if unordered or ordered:
                if current_item:
                    items.append('\n'.join(current_item))
                current_item = [(unordered or ordered).group(2)]
            elif line.strip():
                current_item.append(line[base_indent + 2:])

        if current_item:
            items.append('\n'.join(current_item))

        return Block(
            type=BlockType.LIST,
            content=text,
            metadata={'type': list_type, 'items': items}
        )

    def _parse_quote(self, text: str) -> Optional[Block]:
        """Parse blockquote"""
        lines = text.split('\n')
        if not all(line.strip().startswith('>') or not line.strip() for line in lines):
            return None

        content = '\n'.join(line[1:].strip() if line.strip().startswith('>') else line for line in lines)
        return Block(
            type=BlockType.QUOTE,
            content=content
        )

    def _parse_raw_html(self, text: str) -> Optional[Block]:
        """Parse raw HTML block"""
        if text.strip().startswith('<') and text.strip().endswith('>'):
            return Block(
                type=BlockType.RAW_HTML,
                content=text.strip()
            )
        return None

    def _parse_paragraph(self, text: str) -> Block:
        """Parse paragraph (default)"""
        return Block(
            type=BlockType.PARAGRAPH,
            content=text
        )

    def _parse_yaml(self, text: str) -> Dict[str, Any]:
        """Simple YAML parser for frontmatter"""
        metadata = {}
        for line in text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')
        return metadata

    def _build_toc(self, blocks: List[Block]) -> List[Dict[str, Any]]:
        """Build table of contents from headings"""
        toc = []
        for block in blocks:
            if block.type == BlockType.HEADING:
                anchor = self._slugify(block.content)
                toc.append({
                    'level': block.metadata.get('level', 1),
                    'title': block.content,
                    'anchor': anchor
                })
        return toc

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')

    def render_inline(self, text: str) -> str:
        """Render inline markdown elements"""
        # Math inline (process first to avoid conflicts)
        text = re.sub(r'\$([^$]+)\$', r'<span class="math">\1</span>', text)

        # Images (process before links to avoid conflicts)
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)

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
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

        return text
