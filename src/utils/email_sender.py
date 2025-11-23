"""
Email Sender - Send PDF reports via email
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List

from src.config import (
    EMAIL_SMTP_SERVER,
    EMAIL_SMTP_PORT,
    EMAIL_USERNAME,
    EMAIL_PASSWORD,
    EMAIL_FROM,
    EMAIL_TO
)
from src.utils.logger import get_logger


class EmailSender:
    """Send emails with PDF attachments"""

    def __init__(self):
        self.logger = get_logger('email_sender')

        # Validate configuration
        if not all([EMAIL_SMTP_SERVER, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM, EMAIL_TO]):
            raise ValueError(
                "Email configuration incomplete. Please set: "
                "EMAIL_SMTP_SERVER, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM, EMAIL_TO"
            )

        self.smtp_server = EMAIL_SMTP_SERVER
        self.smtp_port = EMAIL_SMTP_PORT
        self.username = EMAIL_USERNAME
        self.password = EMAIL_PASSWORD
        self.from_email = EMAIL_FROM
        self.to_emails = EMAIL_TO if isinstance(EMAIL_TO, list) else [EMAIL_TO]

        self.logger.info(f"Email sender initialized (SMTP: {self.smtp_server}:{self.smtp_port})")

    def send_daily_report(
        self,
        pdf_path: str,
        date_str: str,
        article_title: str,
        article_description: str,
        num_news: int,
        num_images: int
    ) -> bool:
        """
        Send daily report email with PDF attachment

        Args:
            pdf_path: Path to PDF file
            date_str: Date string (YYYY-MM-DD)
            article_title: Article title
            article_description: Article description
            num_news: Number of news items
            num_images: Number of images generated

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            self.logger.info(f"Sending daily report to {len(self.to_emails)} recipient(s)...")

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"区块链每日观察 - {date_str}"

            # Create email body
            body = self._create_email_body(
                date_str,
                article_title,
                article_description,
                num_news,
                num_images
            )

            msg.attach(MIMEText(body, 'html', 'utf-8'))

            # Attach PDF
            pdf_file = Path(pdf_path)
            if pdf_file.exists():
                with open(pdf_file, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    pdf_attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=pdf_file.name
                    )
                    msg.attach(pdf_attachment)
                self.logger.info(f"Attached PDF: {pdf_file.name} ({pdf_file.stat().st_size / 1024 / 1024:.2f} MB)")
            else:
                self.logger.error(f"PDF file not found: {pdf_path}")
                return False

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                # Enable TLS
                server.starttls()
                self.logger.debug("TLS enabled")

                # Login
                server.login(self.username, self.password)
                self.logger.debug("Logged in successfully")

                # Send
                server.send_message(msg)
                self.logger.info(f"✓ Email sent successfully to: {', '.join(self.to_emails)}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return False

    def _create_email_body(
        self,
        date_str: str,
        title: str,
        description: str,
        num_news: int,
        num_images: int
    ) -> str:
        """Create HTML email body"""

        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'SimSun', 'STSong', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .header .date {{
            margin-top: 10px;
            font-size: 14px;
            opacity: 0.9;
        }}
        .content {{
            background: white;
            padding: 30px;
            border-left: 1px solid #ddd;
            border-right: 1px solid #ddd;
        }}
        .description {{
            font-size: 16px;
            line-height: 1.8;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
        }}
        .stat {{
            text-align: center;
            flex: 1;
        }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        .attachment {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            text-align: center;
        }}
        .attachment-icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .attachment-text {{
            color: #666;
            font-size: 14px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-radius: 0 0 10px 10px;
            border-top: 1px solid #ddd;
            border-left: 1px solid #ddd;
            border-right: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: #667eea;
            color: white !important;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 区块链每日观察</h1>
        <div class="date">{date_str}</div>
    </div>

    <div class="content">
        <h2 style="color: #667eea; margin-top: 0;">今日报告已生成</h2>

        <div class="description">
            {description}
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-number">{num_news}</div>
                <div class="stat-label">新闻条数</div>
            </div>
            <div class="stat">
                <div class="stat-number">{num_images}</div>
                <div class="stat-label">配图张数</div>
            </div>
        </div>

        <h3 style="color: #764ba2;">📄 报告内容</h3>
        <ul style="line-height: 2;">
            <li><strong>封面页</strong> - 报告标题和概述</li>
            <li><strong>目录</strong> - 快速导航</li>
            <li><strong>深度分析</strong> - 详细的行业观察和数据分析</li>
            <li><strong>信息图表</strong> - AI生成的专业可视化图片</li>
            <li><strong>图片索引</strong> - 所有配图汇总</li>
        </ul>

        <div class="attachment">
            <div class="attachment-icon">📎</div>
            <div class="attachment-text">
                PDF 报告已作为附件发送<br>
                <strong>方便直接打开讲解和分享</strong>
            </div>
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <p style="color: #666; font-size: 14px;">
                💡 提示：PDF 报告包含完整的文章内容和精美配图，<br>
                适合打印、演示和分享。
            </p>
        </div>
    </div>

    <div class="footer">
        <p>
            <strong>区块链每日观察</strong> - 自动化生成报告<br>
            Powered by AI | 每日早上 5:00 自动运行
        </p>
        <p style="margin-top: 15px;">
            本邮件由自动化系统发送，如有问题请联系管理员
        </p>
    </div>
</body>
</html>
"""

    def send_test_email(self, test_message: str = "这是一封测试邮件") -> bool:
        """
        Send a test email to verify configuration

        Args:
            test_message: Test message content

        Returns:
            True if sent successfully
        """
        try:
            self.logger.info("Sending test email...")

            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = "测试邮件 - 区块链每日观察系统"

            body = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #667eea;">✓ 邮件配置测试成功</h2>
    <p>{test_message}</p>
    <p style="color: #666; font-size: 14px; margin-top: 30px;">
        SMTP 服务器: {self.smtp_server}:{self.smtp_port}<br>
        发件人: {self.from_email}<br>
        收件人: {', '.join(self.to_emails)}
    </p>
</body>
</html>
"""

            msg.attach(MIMEText(body, 'html', 'utf-8'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            self.logger.info("✓ Test email sent successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send test email: {e}")
            return False
