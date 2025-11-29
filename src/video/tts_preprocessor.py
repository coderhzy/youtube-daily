"""
TTS Preprocessor - Add emotion tags and clean text for Fish Audio TTS
"""

import re
from typing import List, Tuple
from src.utils.logger import get_logger


class TTSPreprocessor:
    """
    Preprocessor for Fish Audio TTS v1.6
    - Add emotion tags
    - Add pauses and breath markers
    - Convert numbers to readable Chinese
    - Fix common typos
    """

    def __init__(self):
        self.logger = get_logger('tts_preprocessor')

        # 常见错别字修正
        self.typo_fixes = {
            '的的': '的',
            '了了': '了',
            '是是': '是',
            '比特比': '比特币',
            '以太仿': '以太坊',
            '区块连': '区块链',
            '加密贷币': '加密货币',
            '去中心画': '去中心化',
        }

        # 数字转中文映射
        self.num_map = {
            '0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
            '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'
        }

        # 单位映射
        self.unit_map = {
            '万': '万', '亿': '亿', '千': '千', '百': '百'
        }

    def process(self, text: str) -> str:
        """
        Process text for TTS

        Args:
            text: Raw script text

        Returns:
            Processed text with emotion tags and corrections
        """
        self.logger.info("Processing text for TTS...")

        # Step 1: 清理 Markdown 格式
        text = self._clean_markdown(text)

        # Step 2: 修正错别字
        text = self._fix_typos(text)

        # Step 3: 转换数字
        text = self._convert_numbers(text)

        # Step 4: 添加情绪标签和停顿
        text = self._add_emotion_tags(text)

        # Step 5: 清理多余空白
        text = self._clean_whitespace(text)

        self.logger.info(f"TTS preprocessing complete, {len(text)} chars")
        return text

    def _clean_markdown(self, text: str) -> str:
        """Remove Markdown formatting and list markers for TTS"""
        # 移除标题标记
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        # 移除粗体
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        # 移除链接
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # 移除分隔线
        text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
        # 移除无序列表标记 (- 或 *)
        text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)
        # 移除有序列表标记 (1. 2. 3. 等)
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        # 移除带括号的序号 (1) (2) 或 （1）（2）
        text = re.sub(r'^[\(（]\d+[\)）]\s*', '', text, flags=re.MULTILINE)
        # 移除行内的序号标记，如 "第一，" "第二，"
        text = re.sub(r'第[一二三四五六七八九十]+[,，、:：]\s*', '', text)
        # 移除 a) b) c) 这种标记
        text = re.sub(r'^[a-zA-Z]\)\s*', '', text, flags=re.MULTILINE)
        # 移除emoji
        text = re.sub(r'[📊🏛️💰🔧💼✨✓⚠️❌✅🎯💡🔥📈📉🚀💎]', '', text)

        return text

    def _fix_typos(self, text: str) -> str:
        """Fix common typos"""
        for wrong, correct in self.typo_fixes.items():
            text = text.replace(wrong, correct)
        return text

    def _convert_numbers(self, text: str) -> str:
        """Convert Arabic numerals to Chinese readable format"""
        # 处理百分比: 20% → 百分之二十
        def convert_percent(match):
            num = match.group(1)
            return f"百分之{self._num_to_chinese(num)}"
        text = re.sub(r'(\d+(?:\.\d+)?)\s*%', convert_percent, text)

        # 处理美元金额: $95000 → 九万五千美元
        def convert_dollar(match):
            num = match.group(1)
            return f"{self._num_to_chinese(num)}美元"
        text = re.sub(r'\$(\d+(?:,\d{3})*(?:\.\d+)?)', convert_dollar, text)

        # 处理带单位的数字: 10万 → 十万
        def convert_with_unit(match):
            num = match.group(1)
            unit = match.group(2)
            return f"{self._num_to_chinese(num)}{unit}"
        text = re.sub(r'(\d+(?:\.\d+)?)(万|亿|千|百)', convert_with_unit, text)

        # 处理日期: 11月28日 → 十一月二十八日
        def convert_date(match):
            month = match.group(1)
            day = match.group(2)
            return f"{self._num_to_chinese(month)}月{self._num_to_chinese(day)}日"
        text = re.sub(r'(\d{1,2})月(\d{1,2})日', convert_date, text)

        # 处理独立数字
        def convert_standalone(match):
            num = match.group(0)
            # 只转换4位以下的数字，避免转换太长的
            if len(num.replace('.', '').replace(',', '')) <= 6:
                return self._num_to_chinese(num)
            return num
        text = re.sub(r'\b\d+(?:\.\d+)?\b', convert_standalone, text)

        return text

    def _num_to_chinese(self, num_str: str) -> str:
        """Convert number string to Chinese"""
        # 移除逗号
        num_str = num_str.replace(',', '')

        # 处理小数
        if '.' in num_str:
            parts = num_str.split('.')
            integer_part = self._integer_to_chinese(parts[0])
            decimal_part = ''.join(self.num_map.get(d, d) for d in parts[1])
            return f"{integer_part}点{decimal_part}"

        return self._integer_to_chinese(num_str)

    def _integer_to_chinese(self, num_str: str) -> str:
        """Convert integer to Chinese"""
        if not num_str or num_str == '0':
            return '零'

        num = int(num_str)

        # 小数字直接映射
        if num < 10:
            return self.num_map.get(str(num), str(num))

        # 10-99
        if num < 100:
            tens = num // 10
            ones = num % 10
            result = ''
            if tens == 1:
                result = '十'
            else:
                result = self.num_map[str(tens)] + '十'
            if ones > 0:
                result += self.num_map[str(ones)]
            return result

        # 100-999
        if num < 1000:
            hundreds = num // 100
            remainder = num % 100
            result = self.num_map[str(hundreds)] + '百'
            if remainder > 0:
                if remainder < 10:
                    result += '零' + self.num_map[str(remainder)]
                else:
                    result += self._integer_to_chinese(str(remainder))
            return result

        # 1000-9999
        if num < 10000:
            thousands = num // 1000
            remainder = num % 1000
            result = self.num_map[str(thousands)] + '千'
            if remainder > 0:
                if remainder < 100:
                    result += '零' + self._integer_to_chinese(str(remainder))
                else:
                    result += self._integer_to_chinese(str(remainder))
            return result

        # 10000以上用万
        if num < 100000000:
            wan = num // 10000
            remainder = num % 10000
            result = self._integer_to_chinese(str(wan)) + '万'
            if remainder > 0:
                if remainder < 1000:
                    result += '零' + self._integer_to_chinese(str(remainder))
                else:
                    result += self._integer_to_chinese(str(remainder))
            return result

        # 亿以上
        yi = num // 100000000
        remainder = num % 100000000
        result = self._integer_to_chinese(str(yi)) + '亿'
        if remainder > 0:
            if remainder < 10000000:
                result += '零' + self._integer_to_chinese(str(remainder))
            else:
                result += self._integer_to_chinese(str(remainder))
        return result

    def _add_emotion_tags(self, text: str) -> str:
        """
        处理文本，不添加情绪标签（会显得突兀）
        只保留自然的停顿处理
        """
        # 不添加任何情绪标签，直接返回原文
        # Fish Audio 会根据文本内容自动调整语气
        return text

    def _clean_whitespace(self, text: str) -> str:
        """Clean extra whitespace"""
        # 多个换行合并为两个
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 去除行首尾空白
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines)
