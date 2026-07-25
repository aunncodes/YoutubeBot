import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def find_font(size, bold=False):
    if bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            pass

    return ImageFont.load_default()


def fit_image(path, size):
    image = Image.open(path).convert("RGBA")
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    return image


def tint_icon(image, color):
    alpha = image.getchannel("A")
    tinted = Image.new("RGBA", image.size, color)
    tinted.putalpha(alpha)
    return tinted


def wrap_title(draw, title, max_width, max_height):
    for size in range(78, 39, -3):
        font = find_font(size, bold=True)
        estimated_width = max(10, int(max_width / (size * 0.56)))
        wrapped = textwrap.fill(title, width=estimated_width)
        box = draw.multiline_textbbox(
            (0, 0),
            wrapped,
            font=font,
            spacing=8,
            align="center",
        )
        width = box[2] - box[0]
        height = box[3] - box[1]

        if width <= max_width and height <= max_height and wrapped.count("\n") <= 3:
            return wrapped, font, width, height

    font = find_font(40, bold=True)
    wrapped = textwrap.fill(title, width=22)
    box = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=8, align="center")
    return wrapped, font, box[2] - box[0], box[3] - box[1]


class RedditTitleCardBuilder:
    def __init__(self, settings):
        self.settings = settings

    def require_asset(self, name):
        path = self.settings.icon_dir / name
        if not path.exists():
            raise FileNotFoundError(f"Missing title-card asset: {path}")
        return path

    def build(self, title, output_dir):
        width = min(self.settings.video_width - 70, 980)
        height = 530
        padding = 30
        card_width = width - 28
        card_height = height - 28

        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            (20, 24, width - 8, height - 8),
            radius=42,
            fill=(0, 0, 0, 95),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(12))
        canvas.alpha_composite(shadow)

        card = Image.new("RGBA", (card_width, card_height), (255, 255, 255, 250))
        mask = Image.new("L", card.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle((0, 0, card_width, card_height), radius=42, fill=255)
        card.putalpha(mask)
        draw = ImageDraw.Draw(card)

        logo = fit_image(self.require_asset("reddit-logo.png"), 105)
        card.alpha_composite(logo, (padding, 24))

        channel_font = find_font(43, bold=True)
        channel_box = draw.textbbox((0, 0), self.settings.channel_name, font=channel_font)
        channel_width = channel_box[2] - channel_box[0]
        draw.text(
            ((card_width - channel_width) / 2, 42),
            self.settings.channel_name,
            font=channel_font,
            fill=(35, 35, 35, 255),
        )

        title_top = 140
        title_height = 270
        title_width = card_width - 100
        wrapped, title_font, rendered_width, rendered_height = wrap_title(
            draw,
            title,
            title_width,
            title_height,
        )
        draw.multiline_text(
            (
                (card_width - rendered_width) / 2,
                title_top + (title_height - rendered_height) / 2,
            ),
            wrapped,
            font=title_font,
            fill=(15, 15, 15, 255),
            spacing=8,
            align="center",
        )

        icon_color = (125, 125, 125, 255)
        metric_font = find_font(31)
        heart = tint_icon(fit_image(self.require_asset("heart.png"), 38), icon_color)
        comment = tint_icon(fit_image(self.require_asset("comment.png"), 38), icon_color)
        metric_y = card_height - 76

        card.alpha_composite(heart, (32, metric_y))
        draw.text((76, metric_y + 1), "99+", font=metric_font, fill=icon_color)
        card.alpha_composite(comment, (190, metric_y))
        draw.text((234, metric_y + 1), "99+", font=metric_font, fill=icon_color)

        canvas.alpha_composite(card, (8, 8))
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "title-card.png"
        canvas.save(path)
        return path
