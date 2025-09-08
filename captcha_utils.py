# captcha_utils.py
import random
import string
from PIL import Image, ImageDraw, ImageFont
import io
import base64

class CaptchaGenerator:
    """简单验证码生成器"""
    
    def __init__(self, width=120, height=40):
        self.width = width
        self.height = height
        # 避免容易混淆的字符
        self.chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    
    def generate_text(self, length=4):
        """生成验证码文本"""
        return ''.join(random.choices(self.chars, k=length))
    
    def generate_image(self, text):
        """生成验证码图片"""
        # 创建图片
        image = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(image)
        
        # 尝试使用系统字体，如果没有则使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # 绘制文字
        text_width = draw.textlength(text, font=font)
        text_height = 24  # 估算高度
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        
        # 随机颜色绘制每个字符
        for i, char in enumerate(text):
            color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
            char_x = x + i * (text_width // len(text))
            # 添加随机偏移
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            draw.text((char_x + offset_x, y + offset_y), char, fill=color, font=font)
        
        # 添加干扰线
        for _ in range(5):
            start = (random.randint(0, self.width), random.randint(0, self.height))
            end = (random.randint(0, self.width), random.randint(0, self.height))
            color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
            draw.line([start, end], fill=color, width=1)
        
        # 添加噪点
        for _ in range(50):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            draw.point((x, y), fill=color)
        
        return image
    
    def generate_captcha(self):
        """生成验证码文本和图片"""
        text = self.generate_text()
        image = self.generate_image(text)
        
        # 转换为base64字符串
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return text, f"data:image/png;base64,{img_base64}"

# 全局验证码生成器实例
captcha_generator = CaptchaGenerator()