"""
Watermark processing using Python3

"""
from io import BytesIO
from flask import Flask, jsonify, request

# Image Manipulation
from PIL import Image, ImageEnhance
import requests

APP = Flask(__name__)

@APP.route("/generate-watermark")
def generate_image():
    """ generate image """
    img = Image.open('image.jpeg')
    mark = Image.open('watermark.png')
    final = watermark(img, mark, 'tile', 0.8)
    final.show()
    #resize_thumb(final).show()
    return jsonify(error=False, message="Ayos!")

def resize_thumb(img):
    """ Resize image """
    baseheight = 300   #in pixels
    hpercent = (baseheight / float(img.size[1]))
    wsize = int((float(img.size[0]) * float(hpercent)))
    img = img.resize((wsize, baseheight), Image.ANTIALIAS)
    return img

def resize_50(img):
    """ Resize image 50 percent"""
    percentage = 0.5
    hsize = float(img.size[1]) * percentage
    wsize = float(img.size[0]) * percentage
    img = img.resize((int(wsize), int(hsize)), Image.ANTIALIAS)
    return img

def reduce_opacity(image, opacity):
    """Returns an image with reduced opacity."""

    assert opacity >= 0 and opacity <= 1
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    else:
        image = image.copy()
    alpha = image.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    image.putalpha(alpha)
    return image

def watermark(img, mark, position, opacity=1):
    """ Adds a watermark to an image. """

    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # create a transparent layer the size of the image and draw the
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))

    # watermark in that layer.
    if position == 'tile':
        start = 0
        for y_pos in range(0, img.size[1], mark.size[1]):
            for x_pos in range(0, img.size[0], mark.size[0]):
                #print (x_pos, y_pos)
                if start == 1:
                    x_pos += 50
                    start = 0
                else:
                    layer.paste(mark, (x_pos, y_pos), mark)
                    start = 1

    elif position == 'scale':
        # scale, but preserve the aspect ratio
        ratio = min(float(img.size[0]) / mark.size[0], float(img.size[1]) / mark.size[1])
        width = int(mark.size[0] * ratio)
        height = int(mark.size[1] * ratio)
        mark = mark.resize((width, height))
        layer.paste(mark, (int((img.size[0] - width) / 2), int((img.size[1] - height) / 2)))
    else:
        layer.paste(mark, position, mark)

    # Compose image with watermark and layer
    return Image.composite(layer, img, layer)


def url_to_image(url):
    """ Retrieve image from url and return image object """
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

# =======================================================
# ################# HTTP Error Handling #################
# =======================================================

@APP.errorhandler(400)
def bad_request(error):
    """ Error handling 400 """
    return jsonify(error=True, status=400, message=error.description), 400

@APP.errorhandler(403)
def page_forbidden(error):
    """ error handling 403 """
    return jsonify(error=True, status=403, message=error.description), 403

@APP.errorhandler(404)
def page_not_found(error):
    """ Error handling 404 """
    return jsonify(error=True, status=404, message=error.description), 404

@APP.errorhandler(405)
def method_not_allowed(error):
    """ error handling 405 """
    return jsonify(error=True, status=405, message=error.description), 405

@APP.errorhandler(500)
def internal_server_error(error):
    """ Error handling 500 """
    return jsonify(error=True, status=500, message=error.description), 500


if __name__ == '__main__':
    APP.run(debug=False)
