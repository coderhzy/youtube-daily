"""
Image Generator using OpenRouter Gemini Image API
"""

from typing import List, Dict, Any
import base64
import os
from pathlib import Path
from openai import OpenAI

from src.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    GEMINI_IMAGE_MODEL
)
from src.utils.logger import get_logger


class ImageGenerator:
    """Generate images based on article content using Gemini Image API"""

    def __init__(self):
        self.logger = get_logger('image_generator')

        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY must be set in environment variables")

        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
        )
        self.model = GEMINI_IMAGE_MODEL
        self.logger.info(f"Image Generator initialized with model: {self.model}")

    def generate_cover_image(
        self,
        cover_prompt: str,
        attractive_title: str,
        date_str: str,
        output_dir: str = "output/images"
    ) -> Dict[str, Any]:
        """
        Generate cover image for YouTube thumbnail

        Args:
            cover_prompt: AI-generated cover image prompt
            attractive_title: Attractive title for the cover
            date_str: Date string (YYYY-MM-DD)
            output_dir: Directory to save image

        Returns:
            Dict with cover image info (path, title, description) or None
        """
        try:
            self.logger.info(f"Generating cover image with title: {attractive_title}")

            # Create output directory
            output_path = Path(output_dir) / date_str
            output_path.mkdir(parents=True, exist_ok=True)

            # Generate cover image
            image_data = self._generate_single_image(cover_prompt)

            if image_data:
                # Save cover image with special naming
                image_filename = f"00_COVER_{self._sanitize_filename(attractive_title)}.png"
                image_path = output_path / image_filename

                with open(image_path, 'wb') as f:
                    f.write(image_data)

                self.logger.info(f"✓ Cover image saved: {image_path}")

                return {
                    'path': str(image_path),
                    'title': attractive_title,
                    'description': f'YouTube封面图: {attractive_title}',
                    'section': 'COVER',
                    'is_cover': True
                }
            else:
                self.logger.warning("Failed to generate cover image")
                return None

        except Exception as e:
            self.logger.error(f"Error generating cover image: {e}")
            return None

    def generate_images_for_article(
        self,
        article_content: str,
        date_str: str,
        output_dir: str = "output/images",
        cover_prompt: str = None,
        attractive_title: str = None
    ) -> List[Dict[str, Any]]:
        """
        Generate images based on article sections

        Args:
            article_content: Full article markdown content
            date_str: Date string (YYYY-MM-DD)
            output_dir: Directory to save images
            cover_prompt: Optional cover image prompt
            attractive_title: Optional attractive title for cover

        Returns:
            List of image info dicts with path, title, description
        """
        try:
            generated_images = []

            # Generate cover image first (if provided)
            if cover_prompt and attractive_title:
                self.logger.info("Generating cover image...")
                cover_image = self.generate_cover_image(
                    cover_prompt=cover_prompt,
                    attractive_title=attractive_title,
                    date_str=date_str,
                    output_dir=output_dir
                )
                if cover_image:
                    generated_images.append(cover_image)

            # Generate content images
            self.logger.info("Analyzing article to generate content image prompts...")

            # Parse article into sections
            sections = self._parse_article_sections(article_content)
            self.logger.info(f"Found {len(sections)} major sections")

            # Limit sections for production (optimal viewing experience)
            sections = sections[:20]  # 生产模式：生成20张图片（每2分钟切换，40分钟视频最佳体验）
            self.logger.info(f"Limited to {len(sections)} sections for optimal viewing experience")

            # Generate prompts for each section
            image_prompts = self._generate_image_prompts(sections, date_str)
            self.logger.info(f"Generated {len(image_prompts)} image prompts")

            # Create output directory
            output_path = Path(output_dir) / date_str
            output_path.mkdir(parents=True, exist_ok=True)

            # Generate content images (start from 01, 02, etc.)
            start_index = 1
            for i, prompt_info in enumerate(image_prompts, start_index):
                try:
                    self.logger.info(f"Generating image {i}/{len(image_prompts)+start_index-1}: {prompt_info['title']}")

                    image_data = self._generate_single_image(prompt_info['prompt'])

                    if image_data:
                        # Save image
                        image_filename = f"{i:02d}_{self._sanitize_filename(prompt_info['title'])}.png"
                        image_path = output_path / image_filename

                        with open(image_path, 'wb') as f:
                            f.write(image_data)

                        generated_images.append({
                            'path': str(image_path),
                            'title': prompt_info['title'],
                            'description': prompt_info['description'],
                            'section': prompt_info['section'],
                            'is_cover': False
                        })

                        self.logger.info(f"✓ Image saved: {image_path}")
                    else:
                        self.logger.warning(f"Failed to generate image for: {prompt_info['title']}")

                except Exception as e:
                    self.logger.error(f"Error generating image {i}: {e}")
                    continue

            self.logger.info(f"Successfully generated {len(generated_images)} images total (including cover)")
            return generated_images

        except Exception as e:
            self.logger.error(f"Error in image generation: {e}")
            return []

    def _parse_article_sections(self, content: str) -> List[Dict[str, str]]:
        """Parse article into major sections"""
        sections = []
        current_section = None
        current_content = []

        for line in content.split('\n'):
            # Detect main section headers (## )
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content)
                    })

                # Start new section
                current_section = line.replace('##', '').strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        # Add last section
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content)
            })

        return sections

    def _generate_image_prompts(self, sections: List[Dict[str, str]], date_str: str) -> List[Dict[str, str]]:
        """Generate image prompts for each section using AI"""
        try:
            # Prepare sections summary
            sections_text = "\n\n".join([
                f"Section {i+1}: {s['title']}\n{s['content'][:500]}..."
                for i, s in enumerate(sections[:6])  # Limit to first 6 sections
            ])

            prompt = f"""根据以下区块链新闻文章的各个板块，为每个板块生成专业的 **YouTube 视频演讲 PPT 风格**信息图表描述。

日期: {date_str}

文章板块:
{sections_text}

要求（适合 YouTube 视频演讲的 PPT 风格）:
1. **16:9 横屏布局** - 适合视频录制和演讲
2. **高对比度配色** - 确保在视频中清晰可见
3. **大号中文标题** - 观众能从远处看清
4. **简洁明了** - 每张图只传达一个核心信息
5. **专业商务风格** - 类似 PowerPoint 演示文稿
6. **图标+数据** - 视觉化呈现关键信息

图片风格参考：
- 类似 TED 演讲的 PPT
- 企业级商业报告
- YouTube 财经频道的演示图表

配色方案：
- 主色：深蓝色/紫色渐变背景
- 强调色：亮绿色（涨）、红色（跌）、金色（重点）
- 文字：白色或浅色（高对比度）

请以JSON格式返回，每个板块一个对象:
[
  {{
    "section": "板块名称",
    "title": "中文标题（将出现在PPT中）",
    "description": "简短描述（用于PDF说明）",
    "prompt": "详细的英文PPT风格图片生成提示词"
  }}
]

Prompt示例格式：
"Create a professional PowerPoint-style slide for YouTube presentation about '[Chinese Title]'.
Layout: 16:9 horizontal, modern business presentation
Background: Gradient from dark blue to purple, professional and clean
Title: Large bold Chinese text '[Chinese Title]' at top center, white color, highly visible
Content: 3 key points with icons (cryptocurrency/blockchain themed), large numbers/statistics, simple charts
Color scheme: Dark gradient background, white text, green for positive data, red for negative, gold for highlights
Icons: Modern, flat design, crypto/blockchain related (Bitcoin symbol, chart icons, etc.)
Style: YouTube presentation ready, high contrast for video recording, suitable for business presentation, clean and professional, similar to TED talk slides"

注意：
- 强调 16:9 横屏布局（YouTube 标准）
- 高对比度（视频录制友好）
- 大号中文标题（演讲可见性）
- 简洁内容（一张图一个重点）"""

            response = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",  # 使用免费模型生成提示词
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )

            result = response.choices[0].message.content

            # Parse JSON response
            import json
            import re

            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
            if json_match:
                result = json_match.group(1)

            prompts = json.loads(result)
            return prompts

        except Exception as e:
            self.logger.error(f"Error generating image prompts: {e}")
            # Fallback: generate simple prompts
            return self._generate_fallback_prompts(sections)

    def _generate_fallback_prompts(self, sections: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Generate YouTube presentation-style prompts with vivid storytelling (fallback when AI generation fails)"""
        prompts = []

        # Vivid storytelling templates for different blockchain topics
        ppt_styles = {
            '市场': 'Professional business person in suit pointing at large digital screen showing Bitcoin price chart with dramatic green arrow going up, modern office setting, excited expression, floating cryptocurrency coins and holograms, dynamic and energetic atmosphere',
            '政策': 'Diverse group of government officials and business leaders sitting around conference table discussing blockchain policy, serious expressions, world map on wall showing global regulations, professional meeting room, documents and laptops on table',
            'DeFi': 'Young tech entrepreneur presenting DeFi concept on futuristic holographic display, floating smart contract symbols and percentage yields, modern startup office, innovative and forward-thinking atmosphere, blockchain network visualization in background',
            'NFT': 'Creative digital artist working on NFT artwork, surrounded by floating digital art pieces and blockchain symbols, colorful and vibrant studio environment, excited expression looking at successful NFT sale notification',
            '技术': 'Team of diverse software engineers collaborating on blockchain technology upgrade, looking at large screens showing network diagrams and code, modern tech office, innovative problem-solving atmosphere, excitement about breakthrough',
            '投融资': 'Business handshake between investor and blockchain startup founder, with floating money symbols and funding round graphics, professional office setting, celebratory atmosphere, venture capital logos in background',
            '行业': 'Conference hall with speaker presenting blockchain industry trends to engaged audience, large presentation screen showing ecosystem growth chart, professional business setting, audience taking notes and looking interested'
        }

        for i, section in enumerate(sections[:5]):  # Limit to 5 images
            title = section['title']

            # Determine topic category
            category_keywords = {
                '市场': ['市场', '价格', '交易', 'BTC', 'ETH', '币'],
                '政策': ['政策', '监管', '合规', '法律', '政府'],
                'DeFi': ['DeFi', '去中心化', '质押', '收益', 'TVL'],
                'NFT': ['NFT', '数字藏品', '艺术品'],
                '技术': ['技术', '升级', '创新', '协议', '网络'],
                '投融资': ['融资', '投资', '资金', 'VC', '轮'],
                '行业': ['行业', '合作', '机构', '生态']
            }

            # Find matching category
            category = '行业'  # default
            for cat, keywords in category_keywords.items():
                if any(kw in title for kw in keywords):
                    category = cat
                    break

            # Get style template
            content_suggestion = ppt_styles.get(category, ppt_styles['行业'])

            # Generate YouTube storytelling prompt optimized for Nano Banana Pro's text rendering
            prompt = f"""Create a professional YouTube presentation image about '{title}' with excellent Chinese text rendering.

**KEY REQUIREMENT: Use Nano Banana Pro's industry-leading multilingual text rendering to include clear, readable Chinese text throughout the image**

Scene Setup (16:9 horizontal):
- {content_suggestion}
- Real people (1-3 business professionals, experts, or presenters)
- Modern professional setting (office, conference room, or presentation hall)
- Dynamic and engaging composition

Text Elements (CRITICAL - Nano Banana Pro excels at this):
- **Large title**: "{title}" in bold Chinese characters (72pt+), prominently displayed on digital screen or backdrop
- **Key data points**: 3-4 Chinese labels with numbers/statistics on floating holographic displays
- **Bullet points**: Short Chinese text phrases highlighting main points
- **Subtitles**: Optional Chinese subtitles or captions for context
- All text must be crystal clear, readable, and properly rendered in Chinese

Visual Composition:
- Professional business people (diverse, showing appropriate emotions)
- Large digital screens/monitors displaying the Chinese title prominently
- Floating holographic UI elements with Chinese text and data
- Modern technology environment (sleek, professional)
- Cryptocurrency/blockchain visual elements (coins, network diagrams, charts)

Text Rendering Quality:
- Use Nano Banana Pro's advanced typography capabilities
- Ensure all Chinese characters are crisp, clear, and professionally typeset
- Text should look like it's from a high-end business presentation
- Multiple text elements at different sizes (title 72pt, data 48pt, labels 36pt)
- Perfect alignment and spacing for Chinese text

Color Scheme:
- Professional gradient background (dark blue #1a1f3a to purple #2d1b4e)
- White text (#FFFFFF) for maximum contrast and readability
- Accent colors: Green #00FF88 (positive), Red #FF4444 (negative), Gold #FFD700 (highlights)
- Modern, clean, high-tech aesthetic

People & Emotion:
- 1-3 professional figures (business attire)
- Appropriate emotions for the topic (excitement, analysis, concern, or enthusiasm)
- Natural poses (presenting, discussing, pointing at screens)
- Diverse representation

Atmosphere:
- Professional business/tech setting
- Cinematic lighting with dramatic accents
- High-end corporate presentation quality
- Suitable for YouTube video thumbnail or background
- Engaging and visually striking

Technical Specs:
- 16:9 aspect ratio (ideal for YouTube)
- High resolution (2K or higher)
- Photorealistic or high-quality digital art style
- Professional business aesthetic
- Optimized for video recording and presentation

Special Focus for Nano Banana Pro:
- Leverage the model's exceptional Chinese text rendering
- Include multiple text elements (title, data, labels, captions)
- Ensure text is central to the composition, not just decorative
- Make the image information-rich with clear Chinese typography
- Professional infographic quality with human elements

Overall: A professional YouTube presentation image that combines engaging human elements with crystal-clear Chinese text rendering, leveraging Nano Banana Pro's superior multilingual typography to create an information-rich, visually striking image perfect for blockchain news presentation."""

            prompts.append({
                'section': title,
                'title': title,
                'description': f"{title}的专业PPT风格可视化",
                'prompt': prompt
            })

        return prompts

    def _generate_single_image(self, prompt: str) -> bytes:
        """
        Generate a single image using Gemini 2.5 Flash Image Preview (Nano Banana)

        This model offers:
        - High-fidelity visual synthesis
        - Context-rich graphics (infographics, diagrams)
        - Industry-leading text rendering
        - Real-time information via Search grounding
        - Support for 2K/4K outputs
        """
        try:
            self.logger.info(f"Generating image with prompt: {prompt[:100]}...")

            # Use raw requests API because OpenAI SDK doesn't parse images field correctly
            import requests
            import base64
            import json

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.7
            }

            response = requests.post(
                OPENROUTER_BASE_URL + "/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code != 200:
                self.logger.error(f"API error: {response.status_code} - {response.text}")
                return None

            result = response.json()

            # Check for images in response
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {})

                # Check images field
                if 'images' in message and len(message['images']) > 0:
                    self.logger.info("Found images in response!")

                    first_image = message['images'][0]
                    if 'image_url' in first_image:
                        image_url = first_image['image_url'].get('url', '')

                        # Handle base64 data URL
                        if image_url.startswith('data:image'):
                            try:
                                # Extract base64 data
                                if 'base64,' in image_url:
                                    base64_data = image_url.split('base64,')[1]
                                    image_data = base64.b64decode(base64_data)
                                    self.logger.info(f"✓ Decoded base64 image ({len(image_data)} bytes)")
                                    return image_data
                            except Exception as e:
                                self.logger.error(f"Failed to decode base64: {e}")
                                return None

                        # Handle HTTP URL
                        elif image_url.startswith('http'):
                            self.logger.info("Downloading from URL...")
                            img_response = requests.get(image_url, timeout=30)
                            if img_response.status_code == 200:
                                self.logger.info(f"✓ Downloaded image ({len(img_response.content)} bytes)")
                                return img_response.content

            self.logger.warning("No image data found in response")
            return None

        except Exception as e:
            self.logger.error(f"Error in image generation: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename"""
        # Remove special characters
        import re
        name = re.sub(r'[^\w\s-]', '', name)
        # Replace spaces with underscores
        name = re.sub(r'[\s]+', '_', name)
        # Limit length
        return name[:50]
