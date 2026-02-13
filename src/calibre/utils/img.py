#!/usr/bin/env python
# License: GPLv3 Copyright: 2015-2019, Kovid Goyal <kovid at kovidgoyal.net>

'''
Simplified image utilities using Pillow only (no Qt/imageops).
'''

from io import BytesIO

from calibre import fit_image


class NotImage(ValueError):
    pass


def normalize_format_name(fmt):
    fmt = fmt.lower()
    if fmt == 'jpg':
        fmt = 'jpeg'
    return fmt


def image_from_data(data):
    '''Load a PIL Image from data bytes.'''
    from PIL import Image
    try:
        img = Image.open(BytesIO(data))
        img.load()
        return img
    except Exception as e:
        raise NotImage(f'Not a valid image: {e}')


def image_to_data(img, fmt='jpeg', compression_quality=95):
    '''Convert a PIL Image to bytes.'''
    fmt = normalize_format_name(fmt)
    buf = BytesIO()
    if fmt == 'jpeg' and img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')
    save_kwargs = {}
    if fmt == 'jpeg':
        save_kwargs['quality'] = compression_quality
    elif fmt == 'png':
        save_kwargs['optimize'] = True
    img.save(buf, format=fmt.upper(), **save_kwargs)
    return buf.getvalue()


def scale_image(data, width=60, height=80, compression_quality=70, as_png=False, preserve_aspect_ratio=True):
    '''Scale image data to fit in width x height box.'''
    img = image_from_data(data)
    if preserve_aspect_ratio:
        scaled, nw, nh = fit_image(img.width, img.height, width, height)
        if scaled:
            img = img.resize((nw, nh))
    else:
        img = img.resize((width, height))
    fmt = 'png' if as_png else 'jpeg'
    return img.width, img.height, image_to_data(img, fmt=fmt, compression_quality=compression_quality)


def image_and_format_from_data(data):
    '''Return (PIL Image, format_string) from data bytes.'''
    from PIL import Image
    img = Image.open(BytesIO(data))
    fmt = img.format or 'JPEG'
    img.load()
    return img, fmt.lower()


def add_borders_to_image(img_data, left=0, top=0, right=0, bottom=0, border_color='#ffffff'):
    '''Add borders to image data, return new image data.'''
    from PIL import Image
    img = image_from_data(img_data)
    new_width = img.width + left + right
    new_height = img.height + top + bottom
    new_img = Image.new(img.mode, (new_width, new_height), border_color)
    new_img.paste(img, (left, top))
    return image_to_data(new_img, fmt='jpeg')


def resize_image(data, width, height):
    '''Resize image to exact dimensions.'''
    img = image_from_data(data)
    img = img.resize((width, height))
    return image_to_data(img)


def resize_to_fit(img, width, height):
    '''Resize PIL Image to fit in width x height, preserving aspect ratio.'''
    scaled, nw, nh = fit_image(img.width, img.height, width, height)
    if scaled:
        return img.resize((nw, nh))
    return img


def encode_jpeg(data, quality=80):
    '''Re-encode image data as JPEG.'''
    img = image_from_data(data)
    return image_to_data(img, fmt='jpeg', compression_quality=quality)


def grayscale_image(data):
    '''Convert image to grayscale.'''
    img = image_from_data(data)
    img = img.convert('L')
    return image_to_data(img)


def null_image():
    '''Return a 1x1 transparent image.'''
    from PIL import Image
    return Image.new('RGBA', (1, 1), (0, 0, 0, 0))


def image_from_path(path):
    '''Load a PIL Image from file path.'''
    with open(path, 'rb') as f:
        return image_from_data(f.read())


def save_image(img, path, fmt='jpeg'):
    '''Save a PIL Image to file path.'''
    data = image_to_data(img, fmt=fmt)
    with open(path, 'wb') as f:
        f.write(data)
