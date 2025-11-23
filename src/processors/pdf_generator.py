"""
PDF Generator - Create professional PDF reports with images
"""

from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from src.utils.logger import get_logger


class PDFGenerator:
    """Generate PDF reports from article content and images"""

    def __init__(self):
        self.logger = get_logger('pdf_generator')

    def generate_pdf(
        self,
        article_data: Dict[str, Any],
        images: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """
        Generate PDF report with ONLY images (no text content)

        Args:
            article_data: Dict with title, content, description, tags (not used, kept for compatibility)
            images: List of image dicts with path, title, description
            output_path: Output PDF file path

        Returns:
            Path to generated PDF file
        """
        try:
            self.logger.info(f"Generating image-only PDF with {len(images)} images...")

            if not images:
                self.logger.warning("No images provided, creating empty PDF")

            # Create simple HTML with only images
            html_content = self._create_images_only_html(images)

            # Generate PDF
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Create minimal CSS for images
            css = self._create_images_only_css()

            # Generate PDF using WeasyPrint
            HTML(string=html_content).write_pdf(
                output_file,
                stylesheets=[CSS(string=css)]
            )

            self.logger.info(f"✓ Image-only PDF generated: {output_file}")
            return str(output_file)

        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            raise

    def _create_images_only_html(self, images: List[Dict[str, Any]]) -> str:
        """
        Create HTML with only images, one image per page

        Args:
            images: List of image dicts with path

        Returns:
            HTML string
        """
        # Sort images: cover first, then content images
        sorted_images = sorted(images, key=lambda x: (not x.get('is_cover', False), x.get('path', '')))

        # Build HTML with one image per page
        image_html_parts = []
        for img in sorted_images:
            img_path = Path(img['path']).resolve()

            # Each image on its own page
            image_html_parts.append(f'''
                <div class="image-page">
                    <img src="file://{img_path}" alt="Generated Image">
                </div>
            ''')

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Blockchain Daily Images</title>
</head>
<body>
    {''.join(image_html_parts)}
</body>
</html>
"""
        return html

    def _create_images_only_css(self) -> str:
        """
        Create minimal CSS for image-only PDF

        Returns:
            CSS string
        """
        return """
        @page {
            size: A4 landscape;
            margin: 0;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 0;
        }

        .image-page {
            width: 100%;
            height: 100%;
            page-break-after: always;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }

        .image-page:last-child {
            page-break-after: auto;
        }

        .image-page img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
        }
        """

    def _create_html_content(
        self,
        article_data: Dict[str, Any],
        images: List[Dict[str, Any]]
    ) -> str:
        """Create HTML content for PDF"""

        title = article_data.get('title', '区块链每日观察')
        description = article_data.get('description', '')
        content = article_data.get('content', '')
        tags = article_data.get('tags', [])
        date = article_data.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Convert Markdown to HTML
        md_html = markdown.markdown(
            content,
            extensions=['extra', 'codehilite', 'toc', 'tables']
        )

        # Insert images into appropriate sections
        html_with_images = self._insert_images_into_content(md_html, images)

        # Create full HTML document
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <!-- Cover Page -->
    <div class="cover-page">
        <div class="cover-content">
            <h1 class="cover-title">{title}</h1>
            <p class="cover-date">{date}</p>
            <p class="cover-description">{description}</p>
            <div class="cover-tags">
                {''.join([f'<span class="tag">{tag}</span>' for tag in tags])}
            </div>
        </div>
        <div class="cover-footer">
            <p>区块链每日观察 | 自动生成报告</p>
            <p>Powered by AI</p>
        </div>
    </div>

    <!-- Table of Contents -->
    <div class="toc-page">
        <h2>目录</h2>
        <div class="toc-content">
            {self._generate_toc(content)}
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        {html_with_images}
    </div>

    <!-- Images Gallery (if any images weren't inserted) -->
    {self._create_images_gallery(images)}

</body>
</html>
"""
        return html

    def _insert_images_into_content(
        self,
        html_content: str,
        images: List[Dict[str, Any]]
    ) -> str:
        """Insert images into appropriate sections of content"""

        # Create a mapping of section titles to images
        section_images = {}
        for img in images:
            section = img.get('section', '')
            if section:
                if section not in section_images:
                    section_images[section] = []
                section_images[section].append(img)

        # Insert images after their corresponding section headers
        result = html_content

        for section_title, imgs in section_images.items():
            # Find the section header in HTML
            # Look for <h2> tags containing the section title
            import re

            # Match h2 tags with the section title
            pattern = f'(<h2[^>]*>.*?{re.escape(section_title)}.*?</h2>)'

            def replace_with_image(match):
                header = match.group(0)
                # Add images after the header
                images_html = '\n'.join([
                    f'''
                    <div class="image-container">
                        <img src="file://{img["path"]}" alt="{img["title"]}" />
                        <p class="image-caption">{img["title"]}</p>
                        <p class="image-description">{img["description"]}</p>
                    </div>
                    '''
                    for img in imgs
                ])
                return f'{header}\n{images_html}\n'

            result = re.sub(pattern, replace_with_image, result, count=1)

        return result

    def _generate_toc(self, markdown_content: str) -> str:
        """Generate table of contents from markdown headers"""
        toc_items = []
        for line in markdown_content.split('\n'):
            if line.startswith('## '):
                title = line.replace('##', '').strip()
                # Remove emoji if present
                title = title.split(' ', 1)[-1] if ' ' in title else title
                toc_items.append(f'<li class="toc-item">{title}</li>')

        return '<ul class="toc-list">' + '\n'.join(toc_items) + '</ul>'

    def _create_images_gallery(self, images: List[Dict[str, Any]]) -> str:
        """Create an images gallery page at the end"""
        if not images:
            return ''

        gallery_html = '''
        <div class="gallery-page">
            <h2>图片索引</h2>
            <div class="gallery-grid">
        '''

        for img in images:
            gallery_html += f'''
            <div class="gallery-item">
                <img src="file://{img["path"]}" alt="{img["title"]}" />
                <p class="gallery-caption">{img["title"]}</p>
            </div>
            '''

        gallery_html += '''
            </div>
        </div>
        '''

        return gallery_html

    def _create_css(self) -> str:
        """Create CSS styling for PDF"""
        return """
        @page {
            size: A4;
            margin: 2cm;
            @bottom-right {
                content: counter(page);
                font-size: 10pt;
                color: #666;
            }
        }

        body {
            font-family: 'SimSun', 'STSong', serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }

        /* Cover Page */
        .cover-page {
            page-break-after: always;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 100vh;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4cm 2cm;
            margin: -2cm;
        }

        .cover-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .cover-title {
            font-size: 36pt;
            font-weight: bold;
            margin-bottom: 1cm;
            line-height: 1.2;
        }

        .cover-date {
            font-size: 18pt;
            margin-bottom: 0.5cm;
            opacity: 0.9;
        }

        .cover-description {
            font-size: 14pt;
            margin-bottom: 1cm;
            opacity: 0.8;
            max-width: 80%;
            margin-left: auto;
            margin-right: auto;
        }

        .cover-tags {
            margin-top: 1cm;
        }

        .tag {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 0.3cm 0.6cm;
            margin: 0.2cm;
            border-radius: 0.3cm;
            font-size: 11pt;
        }

        .cover-footer {
            margin-top: 2cm;
            font-size: 10pt;
            opacity: 0.7;
        }

        /* Table of Contents */
        .toc-page {
            page-break-after: always;
            page-break-before: always;
        }

        .toc-page h2 {
            font-size: 24pt;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.3cm;
            margin-bottom: 1cm;
        }

        .toc-list {
            list-style: none;
            padding: 0;
        }

        .toc-item {
            padding: 0.3cm 0;
            border-bottom: 1px solid #eee;
            font-size: 12pt;
        }

        /* Main Content */
        .main-content {
            page-break-before: always;
        }

        h1 {
            font-size: 24pt;
            color: #667eea;
            margin-top: 1cm;
            margin-bottom: 0.5cm;
            page-break-after: avoid;
        }

        h2 {
            font-size: 18pt;
            color: #764ba2;
            margin-top: 0.8cm;
            margin-bottom: 0.4cm;
            page-break-after: avoid;
            border-left: 4px solid #667eea;
            padding-left: 0.3cm;
        }

        h3 {
            font-size: 14pt;
            color: #555;
            margin-top: 0.6cm;
            margin-bottom: 0.3cm;
            page-break-after: avoid;
        }

        p {
            margin-bottom: 0.4cm;
            text-align: justify;
        }

        /* Images */
        .image-container {
            margin: 1cm 0;
            text-align: center;
            page-break-inside: avoid;
        }

        .image-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 0.2cm;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .image-caption {
            font-weight: bold;
            font-size: 12pt;
            margin-top: 0.3cm;
            color: #667eea;
        }

        .image-description {
            font-size: 10pt;
            color: #666;
            font-style: italic;
            margin-top: 0.2cm;
        }

        /* Gallery */
        .gallery-page {
            page-break-before: always;
        }

        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1cm;
            margin-top: 1cm;
        }

        .gallery-item {
            text-align: center;
        }

        .gallery-item img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 0.2cm;
        }

        .gallery-caption {
            font-size: 10pt;
            margin-top: 0.3cm;
            color: #666;
        }

        /* Lists */
        ul, ol {
            margin-left: 0.8cm;
            margin-bottom: 0.4cm;
        }

        li {
            margin-bottom: 0.2cm;
        }

        /* Blockquotes */
        blockquote {
            border-left: 4px solid #667eea;
            padding-left: 0.5cm;
            margin: 0.5cm 0;
            font-style: italic;
            background: #f8f9fa;
            padding: 0.5cm;
            border-radius: 0.2cm;
        }

        /* Code */
        code {
            background: #f4f4f4;
            padding: 0.1cm 0.2cm;
            border-radius: 0.1cm;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 0.5cm 0;
            page-break-inside: avoid;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 0.3cm;
            text-align: left;
        }

        th {
            background: #667eea;
            color: white;
            font-weight: bold;
        }

        tr:nth-child(even) {
            background: #f8f9fa;
        }
        """
