import io
from typing import Tuple
import random
from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET
import base64
import math

class AvatarGenerator:
    # 预定义的颜色方案
    COLORS = [
        ('#FF6B6B', '#FFE66D'),  # 红色背景，黄色图标
        ('#4ECDC4', '#FFFFFF'),  # 青色背景，白色图标
        ('#45B7D1', '#FFFFFF'),  # 蓝色背景，白色图标
        ('#96CEB4', '#FFFFFF'),  # 绿色背景，白色图标
        ('#D4A5A5', '#FFFFFF'),  # 粉色背景，白色图标
    ]
    
    # Font Awesome SVG 路径数据
    ANIMAL_ICONS = {
        'dog': 'M576 840c-35.3 0-64-28.7-64-64s28.7-64 64-64s64 28.7 64 64s-28.7 64-64 64zm160-128c-35.3 0-64-28.7-64-64s28.7-64 64-64s64 28.7 64 64s-28.7 64-64 64zm160-128c-35.3 0-64-28.7-64-64s28.7-64 64-64s64 28.7 64 64s-28.7 64-64 64z',
        'cat': 'M320 192h17.1c22.1 38.3 63.5 64 110.9 64s88.8-25.7 110.9-64H576c35.3 0 64-28.7 64-64V64c0-35.3-28.7-64-64-64H320c-35.3 0-64 28.7-64 64v64c0 35.3 28.7 64 64 64zM44.1 224a384 384 0 0 0 791.8 0H44.1z',
        'fish': 'M0 256c0 71 57.3 128 128 128s128-57.3 128-128S199 128 128 128S0 185.3 0 256zm384 0c0 35.3 28.7 64 64 64s64-28.7 64-64s-28.7-64-64-64s-64 28.7-64 64z',
        'paw': 'M256 128c0 53-43 96-96 96s-96-43-96-96s43-96 96-96s96 43 96 96zM0 256C0 203 43 160 96 160s96 43 96 96s-43 96-96 96s-96-43-96-96zm352-32c53 0 96 43 96 96s-43 96-96 96s-96-43-96-96s43-96 96-96z'
    }

    @classmethod
    def draw_fallback_icon(cls, draw: ImageDraw.Draw, size: Tuple[int, int], species: str, color: str):
        """
        绘制备选图标（不依赖外部资源）
        """
        width, height = size
        margin = min(width, height) // 4
        
        if species == 'dog':
            # 简单的狗头轮廓
            # 头部
            draw.ellipse([margin, margin, width-margin, height-margin], outline=color, width=width//20)
            # 耳朵
            ear_size = margin // 2
            draw.ellipse([margin, margin-ear_size, margin+ear_size, margin], fill=color)
            draw.ellipse([width-margin-ear_size, margin-ear_size, width-margin, margin], fill=color)
            
        elif species == 'cat':
            # 简单的猫头轮廓
            # 头部
            draw.ellipse([margin, margin, width-margin, height-margin], outline=color, width=width//20)
            # 尖耳朵
            points = [
                (margin, margin),  # 左耳尖
                (margin+margin//2, margin+margin//2),  # 左耳底
                (width-margin-margin//2, margin+margin//2),  # 右耳底
                (width-margin, margin),  # 右耳尖
            ]
            draw.line(points, fill=color, width=width//20)
            
        elif species == 'fish':
            # 简单的鱼形
            # 身体
            draw.ellipse([margin, margin, width-margin, height-margin], outline=color, width=width//20)
            # 尾巴
            points = [
                (width-margin, height//2),  # 尾巴连接点
                (width-margin//2, height//2-margin//2),  # 上尾尖
                (width-margin//2, height//2+margin//2),  # 下尾尖
            ]
            draw.polygon(points, fill=color)
            
        else:
            # 默认爪印
            center_x, center_y = width//2, height//2
            pad_radius = min(width, height) // 6
            
            # 中心圆
            draw.ellipse(
                [center_x-pad_radius, center_y-pad_radius,
                 center_x+pad_radius, center_y+pad_radius],
                outline=color, width=width//30
            )
            
            # 四个脚趾
            for angle in [45, 135, 225, 315]:
                rad = math.radians(angle)
                offset = pad_radius * 1.5
                x = center_x + offset * math.cos(rad)
                y = center_y + offset * math.sin(rad)
                r = pad_radius * 0.7
                draw.ellipse(
                    [x-r, y-r, x+r, y+r],
                    outline=color, width=width//30
                )

    @classmethod
    def generate_default_avatar(
        cls,
        size: Tuple[int, int] = (200, 200),
        species: str = None
    ) -> bytes:
        """
        Generate a default avatar
        """
        # 创建新图片
        img = Image.new('RGB', size)
        draw = ImageDraw.Draw(img)
        
        # 随机选择颜色方案
        bg_color, icon_color = random.choice(cls.COLORS)
        
        # 填充背景
        draw.rectangle([0, 0, size[0], size[1]], fill=bg_color)
        
        try:
            # 尝试使用 SVG 路径
            path_data = cls.ANIMAL_ICONS.get(species.lower() if species else None, cls.ANIMAL_ICONS['paw'])
            
            # 创建 SVG
            svg = ET.Element('svg')
            svg.set('width', str(size[0]))
            svg.set('height', str(size[1]))
            svg.set('viewBox', '0 0 512 512')
            
            path = ET.SubElement(svg, 'path')
            path.set('d', path_data)
            path.set('fill', icon_color)
            
            # 转换并绘制
            svg_str = ET.tostring(svg)
            img_data = f"data:image/svg+xml;base64,{base64.b64encode(svg_str).decode()}"
            
            with Image.open(io.BytesIO(base64.b64decode(img_data.split(',')[1]))) as icon:
                icon_size = min(size) // 2
                icon = icon.resize((icon_size, icon_size))
                x = (size[0] - icon_size) // 2
                y = (size[1] - icon_size) // 2
                img.paste(icon, (x, y), icon)
                
        except Exception:
            # 如果 SVG 转换失败，使用备选图标
            cls.draw_fallback_icon(draw, size, species.lower() if species else 'paw', icon_color)
        
        # 转换为字节流
        output = io.BytesIO()
        img.save(output, format='PNG', optimize=True)
        return output.getvalue() 