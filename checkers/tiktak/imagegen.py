import subprocess

from PIL import Image, ImageDraw, ImageFont

template_path = 'template.png'


def get_text_image(message, output_path):
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("micross.ttf", 28)

    (x, y) = (10, 10)

    color = 'rgb(0, 0, 0)'

    draw.text((x, y), message, fill=color, font=font, spacing=100)

    output_path = output_path + ".png"

    img.save(output_path)
    return output_path


def get_text_webm(message, output_path):
    png_path = get_text_image(message, output_path)
    webm_path = output_path + ".webm"
    subprocess.check_output(["ffmpeg", "-y", "-framerate", "0.5", "-i", png_path, "-vf", "format=yuv420p", webm_path])
    return webm_path
