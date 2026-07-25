import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def find_font(size, bold=False):
    candidates = []

    if bold:
        candidates.extend(
            [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/System/Library/Fonts/Supplemental/Helvetica.ttc",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/Library/Fonts/Arial Bold.ttf",
                "/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/System/Library/Fonts/Supplemental/Helvetica.ttc",
                "/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ]
        )

    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            pass

    return ImageFont.load_default()


def measure_multiline(draw, text, font, spacing):
    left, top, right, bottom = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=spacing,
        align="center",
    )
    return right - left, bottom - top


def wrap_title(draw, title, max_width):
    size = 82
    lines = []

    while size >= 40:
        font = find_font(size, bold=True)
        target = max(2, int(max_width / max(1, size * 0.64)))
        wrapped = textwrap.fill(title, width=target)
        width, height = measure_multiline(draw, wrapped, font, 10)
        line_count = wrapped.count("\n") + 1

        if width <= max_width and line_count <= 3 and height <= 300:
            return wrapped, font

        size -= 4

    return textwrap.fill(title, width=18), find_font(40, bold=True)


def draw_reddit_logo(draw, x, y, size):
    orange = (255, 87, 34, 255)
    white = (255, 255, 255, 255)
    outline = (255, 255, 255, 255)
    black = (35, 35, 35, 255)

    draw.ellipse((x, y, x + size, y + size), fill=orange)

    face_w = int(size * 0.54)
    face_h = int(size * 0.38)
    face_x = x + int(size * 0.23)
    face_y = y + int(size * 0.38)
    draw.rounded_rectangle(
        (face_x, face_y, face_x + face_w, face_y + face_h),
        radius=int(face_h * 0.45),
        fill=white,
    )

    eye_y = face_y + int(face_h * 0.34)
    eye_r = max(2, int(size * 0.03))
    left_eye_x = face_x + int(face_w * 0.30)
    right_eye_x = face_x + int(face_w * 0.70)
    draw.ellipse((left_eye_x - eye_r, eye_y - eye_r, left_eye_x + eye_r, eye_y + eye_r), fill=black)
    draw.ellipse((right_eye_x - eye_r, eye_y - eye_r, right_eye_x + eye_r, eye_y + eye_r), fill=black)

    mouth_box = (
        face_x + int(face_w * 0.25),
        face_y + int(face_h * 0.43),
        face_x + int(face_w * 0.75),
        face_y + int(face_h * 0.90),
    )
    draw.arc(mouth_box, start=15, end=165, fill=black, width=max(2, int(size * 0.02)))

    antenna_start = (face_x + int(face_w * 0.62), face_y - int(size * 0.04))
    antenna_mid = (x + int(size * 0.67), y + int(size * 0.18))
    antenna_end = (x + int(size * 0.84), y + int(size * 0.16))
    draw.line((antenna_start, antenna_mid, antenna_end), fill=outline, width=max(3, int(size * 0.03)))
    orb_r = max(4, int(size * 0.06))
    draw.ellipse(
        (
            antenna_end[0] - orb_r,
            antenna_end[1] - orb_r,
            antenna_end[0] + orb_r,
            antenna_end[1] + orb_r,
        ),
        outline=outline,
        width=max(2, int(size * 0.02)),
        fill=orange,
    )


def draw_bottom_metrics(draw, x, y, font):
    color = (128, 128, 128, 255)

    draw.text((x, y), "♡", font=font, fill=color)
    draw.text((x + 36, y), "99+", font=font, fill=color)

    bubble_x = x + 180
    bubble_y = y + 7
    bubble_w = 28
    bubble_h = 22
    draw.rounded_rectangle(
        (bubble_x, bubble_y, bubble_x + bubble_w, bubble_y + bubble_h),
        radius=7,
        outline=color,
        width=2,
    )
    draw.polygon(
        [
            (bubble_x + 8, bubble_y + bubble_h),
            (bubble_x + 12, bubble_y + bubble_h + 8),
            (bubble_x + 18, bubble_y + bubble_h),
        ],
        outline=color,
        fill=None,
    )
    draw.text((bubble_x + 44, y), "99+", font=font, fill=color)


class RedditTitleCardBuilder:
    def __init__(self, settings):
        self.settings = settings

    def build(self, title, output_dir):
        width = min(self.settings.video_width - 70, 980)
        height = 540
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle(
            (16, 20, width - 16, height - 20),
            radius=42,
            fill=(0, 0, 0, 88),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        canvas.alpha_composite(shadow)

        card = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(card)
        draw.rounded_rectangle(
            (0, 0, width - 32, height - 32),
            radius=42,
            fill=(255, 255, 255, 245),
        )

        logo_x = 26
        logo_y = 26
        logo_size = 110
        draw_reddit_logo(draw, logo_x, logo_y, logo_size)

        channel_font = find_font(42, bold=True)
        channel_text = self.settings.channel_name
        channel_box = draw.textbbox((0, 0), channel_text, font=channel_font)
        channel_width = channel_box[2] - channel_box[0]
        channel_x = (width - 32 - channel_width) / 2
        draw.text((channel_x, 34), channel_text, font=channel_font, fill=(32, 32, 32, 255))

        title_area_x = 48
        title_area_y = 145
        title_area_w = width - 128
        title_area_h = 260
        wrapped_title, title_font = wrap_title(draw, title, title_area_w)
        title_width, title_height = measure_multiline(draw, wrapped_title, title_font, 8)
        title_x = (width - 32 - title_width) / 2
        title_y = title_area_y + max(0, (title_area_h - title_height) / 2)
        draw.multiline_text(
            (title_x, title_y),
            wrapped_title,
            font=title_font,
            fill=(16, 16, 16, 255),
            spacing=8,
            align="center",
        )

        metrics_font = find_font(30, bold=False)
        draw_bottom_metrics(draw, 34, height - 94, metrics_font)

        canvas.alpha_composite(card, (16, 16))
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "title-card.png"
        canvas.save(path)
        return path
