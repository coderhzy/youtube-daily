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

    def generate_images_for_article(
        self,
        article_content: str,
        date_str: str,
        output_dir: str = "output/images"
    ) -> List[Dict[str, Any]]:
        """
        Generate images based on article sections

        Args:
            article_content: Full article markdown content
            date_str: Date string (YYYY-MM-DD)
            output_dir: Directory to save images

        Returns:
            List of image info dicts with path, title, description
        """
        try:
            self.logger.info("Analyzing article to generate image prompts...")

            # Parse article into sections
            sections = self._parse_article_sections(article_content)
            self.logger.info(f"Found {len(sections)} major sections")

            # Generate prompts for each section
            image_prompts = self._generate_image_prompts(sections, date_str)
            self.logger.info(f"Generated {len(image_prompts)} image prompts")

            # Create output directory
            output_path = Path(output_dir) / date_str
            output_path.mkdir(parents=True, exist_ok=True)

            # Generate images
            generated_images = []
            for i, prompt_info in enumerate(image_prompts, 1):
                try:
                    self.logger.info(f"Generating image {i}/{len(image_prompts)}: {prompt_info['title']}")

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
                            'section': prompt_info['section']
                        })

                        self.logger.info(f"✓ Image saved: {image_path}")
                    else:
                        self.logger.warning(f"Failed to generate image for: {prompt_info['title']}")

                except Exception as e:
                    self.logger.error(f"Error generating image {i}: {e}")
                    continue

            self.logger.info(f"Successfully generated {len(generated_images)} images")
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

            prompt = f"""根据以下区块链新闻文章的各个板块，为每个板块生成专业的信息图表描述，用于 Nano Banana Pro (Gemini 3 Pro Image) 生成高质量视觉化图片。

日期: {date_str}

文章板块:
{sections_text}

要求（充分利用 Nano Banana Pro 的特性）:
1. 为每个主要板块生成一个专业信息图表描述
2. 图片风格：现代商业信息图表、数据可视化、专业演示级别
3. 必须包含：
   - 清晰的中文标题文字（Nano Banana Pro 支持高质量多语言文字渲染）
   - 关键数据和数字的可视化（图表、数据点、百分比）
   - 专业配色方案（蓝色/绿色科技感或橙色/红色警示）
   - 图标和符号（区块链、加密货币相关）
   - 清晰的层次结构和布局
4. 适合打印和演示使用（高分辨率、专业排版）
5. 每张图片聚焦一个核心主题

请以JSON格式返回，每个板块一个对象:
[
  {{
    "section": "板块名称",
    "title": "中文标题（将出现在图片中）",
    "description": "简短描述（用于PDF说明文字）",
    "prompt": "详细的英文图片生成提示词，包含：layout, typography, color scheme, data visualization elements, icons, text content"
  }}
]

Prompt示例格式：
"Create a professional infographic titled '[Chinese Title]' about [topic]. Layout: vertical composition with header, 3-4 data sections, and footer. Include: bold Chinese title at top, key statistics with large numbers and icons, trend charts/graphs, modern blue-green color gradient, clean white background, professional business style. Text: clearly readable Chinese labels and numbers. Style: minimalist, data-driven, presentation-ready."

注意：
- prompt 必须是详细的英文描述
- 明确指定要包含的中文文字内容
- 描述具体的布局、颜色、图表类型
- 强调专业性和可读性"""

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
        """Generate simple fallback prompts if AI generation fails"""
        prompts = []
        for i, section in enumerate(sections[:5]):  # Limit to 5 images
            prompts.append({
                'section': section['title'],
                'title': f"{section['title']} - 视觉化",
                'description': f"{section['title']}的关键信息可视化",
                'prompt': f"Professional infographic about {section['title']} in blockchain industry, modern design, data visualization, clean layout, business style"
            })
        return prompts

    def _generate_single_image(self, prompt: str) -> bytes:
        """
        Generate a single image using Nano Banana Pro (Gemini 3 Pro Image Preview)

        This model offers:
        - High-fidelity visual synthesis
        - Context-rich graphics (infographics, diagrams)
        - Industry-leading text rendering
        - Real-time information via Search grounding
        - Support for 2K/4K outputs
        """
        try:
            self.logger.info(f"Generating image with prompt: {prompt[:100]}...")

            # Call Gemini 3 Pro Image Preview via OpenRouter
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                # Nano Banana Pro specific parameters
                max_tokens=4000,
                temperature=0.7
            )

            # Extract image data from response
            # The response format may vary, check OpenRouter docs for exact format
            result = response.choices[0].message.content

            # If the model returns a URL or base64 data, handle accordingly
            if result:
                # Try to extract image data
                # This might be a URL or base64 encoded image
                import requests
                import base64

                # Check if it's a URL
                if result.startswith('http'):
                    self.logger.info("Downloading image from URL...")
                    img_response = requests.get(result, timeout=30)
                    if img_response.status_code == 200:
                        return img_response.content
                    else:
                        self.logger.error(f"Failed to download image: {img_response.status_code}")
                        return None

                # Check if it's base64
                elif 'base64' in result.lower() or len(result) > 1000:
                    try:
                        # Extract base64 data (remove data:image/png;base64, prefix if present)
                        if 'base64,' in result:
                            result = result.split('base64,')[1]
                        image_data = base64.b64decode(result)
                        return image_data
                    except Exception as e:
                        self.logger.error(f"Failed to decode base64 image: {e}")
                        return None
                else:
                    self.logger.warning("Unexpected response format from image generation API")
                    self.logger.debug(f"Response: {result[:200]}")
                    return None
            else:
                self.logger.warning("Empty response from image generation API")
                return None

        except Exception as e:
            self.logger.error(f"Error in single image generation: {e}")
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
