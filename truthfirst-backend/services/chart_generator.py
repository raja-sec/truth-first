"""
Chart Generator Service
Creates confidence visualization charts for PDF reports.
"""

import io
import base64
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt


class ChartGenerator:
    """Service for generating confidence charts."""
    
    @staticmethod
    def generate_confidence_gauge(confidence: float, verdict: str) -> str:
        """
        Generate donut chart (Deepfake vs Genuine) as base64 PNG
        """

        percent = int(confidence * 100)
        remainder = 100 - percent

        if verdict in ["DEEPFAKE", "PHISHING"]:
            values = [percent, remainder]
            colors = ["#ef4444", "#b8edc8"]  # Deepfake, Genuine
            bg_color = "#fef2f2"             # Light red
        else:
            values = [percent, remainder]
            colors = ["#10b981", "#edbaba"]  # Genuine, Risk
            bg_color = "#f0fdf4"             # Light green
            
        

        # ---- SIZE CONTROL (see section 2) ----
        fig, ax = plt.subplots(figsize=(2.8, 2.8), dpi=200)

        # Background color (VERY IMPORTANT)
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        ax.pie(
            values,
            startangle=90,
            counterclock=False,
            colors=colors,
            wedgeprops=dict(width=0.38, edgecolor=bg_color)
        )

        ax.set(aspect="equal")
        ax.axis("off")

        buffer = io.BytesIO()
        plt.savefig(
            buffer,
            format="png",
            dpi=200,
            bbox_inches="tight",
            facecolor=fig.get_facecolor()
        )
        plt.close(fig)

        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

    
    @staticmethod
    def generate_simple_bar(
        confidence: float,
        verdict: str,
        size: Tuple[int, int] = (400, 100)
    ) -> str:
        """
        Generate a simple confidence bar as base64.
        
        Args:
            confidence: Confidence value (0.0 to 1.0)
            verdict: Verdict string
            size: Image size (width, height)
            
        Returns:
            Base64 encoded PNG image
        """
        width, height = size
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Colors
        if verdict in ['DEEPFAKE', 'PHISHING']:
            bar_color = '#ef4444'
            bg_color = '#fef2f2'
        else:
            bar_color = '#10b981'
            bg_color = '#f0fdf4'
        
        # Background
        draw.rectangle([0, 0, width, height], fill=bg_color)
        
        # Bar background (gray)
        bar_height = 30
        bar_y = (height - bar_height) // 2
        draw.rectangle([20, bar_y, width - 20, bar_y + bar_height], fill='#e5e7eb')
        
        # Confidence bar (colored)
        bar_width = int((width - 40) * confidence)
        draw.rectangle([20, bar_y, 20 + bar_width, bar_y + bar_height], fill=bar_color)
        
        # Text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except:
            font = ImageFont.load_default()
        
        text = f"{verdict}: {int(confidence * 100)}%"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        draw.text(
            (width // 2 - text_width // 2, bar_y + bar_height + 10),
            text,
            fill='#1f2937',
            font=font
        )
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')