#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_residence_card():
    # 400x250の画像を作成
    width, height = 400, 250
    image = Image.new('RGB', (width, height), color='lightblue')
    
    # 描画オブジェクトを作成
    draw = ImageDraw.Draw(image)
    
    # テキストを追加
    try:
        # デフォルトフォントを使用
        font = ImageFont.load_default()
    except:
        font = None
    
    # テキストを描画
    text1 = "サンプル在留カード"
    text2 = "(Sample Residence Card)"
    
    # テキストサイズを取得
    if font:
        text1_bbox = draw.textbbox((0, 0), text1, font=font)
        text2_bbox = draw.textbbox((0, 0), text2, font=font)
        text1_width = text1_bbox[2] - text1_bbox[0]
        text1_height = text1_bbox[3] - text1_bbox[1]
        text2_width = text2_bbox[2] - text2_bbox[0]
        text2_height = text2_bbox[3] - text2_bbox[1]
    else:
        text1_width, text1_height = 200, 20
        text2_width, text2_height = 180, 15
    
    # テキストを中央に配置
    text1_x = (width - text1_width) // 2
    text1_y = (height - text1_height) // 2 - 20
    text2_x = (width - text2_width) // 2
    text2_y = (height - text2_height) // 2 + 10
    
    # テキストを描画
    draw.text((text1_x, text1_y), text1, fill='black', font=font)
    draw.text((text2_x, text2_y), text2, fill='darkblue', font=font)
    
    # 枠線を描画
    draw.rectangle([10, 10, width-10, height-10], outline='darkblue', width=3)
    
    # 保存
    output_path = 'static/uploads/sample_residence_card.jpg'
    image.save(output_path, 'JPEG', quality=95)
    print(f"✓ Sample residence card image created: {output_path}")
    
    return output_path

if __name__ == "__main__":
    create_sample_residence_card()