import subprocess

from PIL import Image, ImageDraw, ImageFont


font_name = 'ocr-aregular.ttf'
font_size = 37

def get_text_image(message, output_path):

    font = ImageFont.truetype(font_name, font_size)

    (w, h) = font.getsize(message)

    img = Image.new('RGB', (w + 20, h + 200), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    (x, y) = (10, 100)

    color = 'rgb(0, 0, 0)'

    draw.text((x, y), message, fill=color, font=font)

    output_path = output_path + ".png"

    img.save(output_path)
    return output_path


def get_text_webm(message, output_path):
    png_path = get_text_image(message, output_path)
    webm_path = output_path + ".webm"
    subprocess.run(["ffmpeg", "-y", "-framerate", "0.5", "-i", png_path, "-vf", "format=yuv420p", webm_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return webm_path
