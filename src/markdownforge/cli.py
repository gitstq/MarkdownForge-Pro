"""
Command-line interface for MarkdownForge
"""

import os
import sys
import argparse
import time
from pathlib import Path
from typing import Optional, List

from .core import MarkdownProcessor
from .enhancers import (
    TOCEnhancer, CodeHighlightEnhancer, MathEnhancer,
    AnchorEnhancer, LinkEnhancer, ImageEnhancer
)
from .exporters import HTMLExporter, PDFExporter, WordExporter
from .watcher import FileWatcher


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog='markdownforge',
        description='🚀 MarkdownForge-Pro - Lightweight Terminal Markdown Document Intelligence Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  markdownforge input.md                    # Convert to HTML
  markdownforge input.md -o output.html     # Specify output
  markdownforge input.md -f pdf             # Export as PDF
  markdownforge input.md --toc              # Add table of contents
  markdownforge input.md --watch            # Watch for changes
  markdownforge input.md --serve            # Start preview server
        '''
    )

    parser.add_argument(
        'input',
        help='Input markdown file'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output file path'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['html', 'pdf', 'docx', 'word'],
        default='html',
        help='Output format (default: html)'
    )

    parser.add_argument(
        '--toc',
        action='store_true',
        help='Add table of contents'
    )

    parser.add_argument(
        '--toc-depth',
        type=int,
        default=6,
        help='Maximum depth for TOC (default: 6)'
    )

    parser.add_argument(
        '--no-highlight',
        action='store_true',
        help='Disable syntax highlighting'
    )

    parser.add_argument(
        '--math',
        choices=['katex', 'mathjax', 'none'],
        default='katex',
        help='Math renderer (default: katex)'
    )

    parser.add_argument(
        '--theme',
        default='default',
        help='Theme name (default: default)'
    )

    parser.add_argument(
        '--standalone',
        action='store_true',
        default=True,
        help='Generate standalone HTML (default: True)'
    )

    parser.add_argument(
        '--no-standalone',
        action='store_true',
        help='Generate HTML without wrapper'
    )

    parser.add_argument(
        '-w', '--watch',
        action='store_true',
        help='Watch for file changes and rebuild'
    )

    parser.add_argument(
        '-s', '--serve',
        action='store_true',
        help='Start preview server'
    )

    parser.add_argument(
        '-p', '--port',
        type=int,
        default=8080,
        help='Server port (default: 8080)'
    )

    parser.add_argument(
        '--open',
        action='store_true',
        help='Open browser after starting server'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    return parser


def process_file(
    input_path: str,
    output_path: Optional[str],
    format: str,
    options: dict
) -> str:
    """Process markdown file and export"""
    # Read input file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create processor
    processor = MarkdownProcessor()

    # Add enhancers
    processor.add_enhancer(AnchorEnhancer())

    if options.get('toc'):
        processor.add_enhancer(TOCEnhancer(max_depth=options.get('toc_depth', 6)))

    if not options.get('no_highlight'):
        processor.add_enhancer(CodeHighlightEnhancer())

    if options.get('math') != 'none':
        processor.add_enhancer(MathEnhancer(renderer=options.get('math', 'katex')))

    # Process document
    doc = processor.process(content)

    # Export
    if format in ['html']:
        standalone = not options.get('no_standalone', False)
        exporter = HTMLExporter(theme=options.get('theme', 'default'), standalone=standalone)
    elif format in ['pdf']:
        exporter = PDFExporter(theme=options.get('theme', 'default'))
    elif format in ['docx', 'word']:
        exporter = WordExporter(theme=options.get('theme', 'default'))
    else:
        raise ValueError(f"Unsupported format: {format}")

    # Determine output path
    if not output_path:
        base = os.path.splitext(input_path)[0]
        if format == 'docx':
            output_path = f"{base}.docx.html"
        else:
            output_path = f"{base}.{format if format != 'word' else 'docx.html'}"

    # Export
    result = exporter.export(doc, output_path)

    return output_path


def serve_file(file_path: str, port: int, open_browser: bool = False):
    """Start HTTP server for preview"""
    import http.server
    import socketserver
    import webbrowser
    import threading

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=os.path.dirname(file_path) or '.', **kwargs)

        def log_message(self, format, *args):
            # Suppress log messages
            pass

    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            filename = os.path.basename(file_path)
            url = f"http://localhost:{port}/{filename}"

            print(f"🌐 Server started at {url}")
            print("Press Ctrl+C to stop")

            if open_browser:
                threading.Timer(1.0, lambda: webbrowser.open(url)).start()

            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Server stopped")
    except OSError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


def watch_file(
    input_path: str,
    output_path: str,
    format: str,
    options: dict
):
    """Watch file for changes and rebuild"""
    print(f"👀 Watching {input_path} for changes...")
    print("Press Ctrl+C to stop")

    def rebuild():
        try:
            result = process_file(input_path, output_path, format, options)
            print(f"✅ Rebuilt: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Initial build
    rebuild()

    # Watch for changes
    watcher = FileWatcher(input_path, rebuild)
    watcher.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        watcher.stop()
        print("\n✋ Watch stopped")


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point"""
    parser = create_parser()
    parsed = parser.parse_args(args)

    # Validate input
    if not os.path.exists(parsed.input):
        print(f"❌ Error: File not found: {parsed.input}")
        return 1

    # Build options
    options = {
        'toc': parsed.toc,
        'toc_depth': parsed.toc_depth,
        'no_highlight': parsed.no_highlight,
        'math': parsed.math,
        'theme': parsed.theme,
        'no_standalone': parsed.no_standalone,
    }

    try:
        if parsed.watch:
            watch_file(
                parsed.input,
                parsed.output,
                parsed.format,
                options
            )
        elif parsed.serve:
            output_path = process_file(
                parsed.input,
                parsed.output,
                parsed.format,
                options
            )
            serve_file(output_path, parsed.port, parsed.open)
        else:
            output_path = process_file(
                parsed.input,
                parsed.output,
                parsed.format,
                options
            )
            print(f"✅ Generated: {output_path}")

        return 0

    except Exception as e:
        if parsed.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
