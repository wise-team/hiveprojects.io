import logging
import os
import time
import urllib
import uuid
from distutils.version import LooseVersion as versioner
from os import makedirs
from os.path import join, split, exists, splitext

from PIL import Image
from django.conf import settings
from django.db import models
from requests.compat import quote

logger = logging.getLogger(__name__)

#this is gross, but requests doesn't import quote_plus into compat,
#so we re-implement it here
def quote_plus(s, safe=''):
    """Quote the query fragment of a URL; replacing ' ' with '+'"""
    if ' ' in s:
        s = quote(s, safe + ' ')
        return s.replace(' ', '+')
    return quote(s, safe)


def uniquer(seq, idfun=None):
    if idfun is None:
        def idfun(x):
            return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


def get_version(package):

    versions = package.version_set.exclude(upload_time=None)
    try:
        return versions.latest()
    except models.ObjectDoesNotExist:
        return None


def get_pypi_version(package):
    versions = []
    for v_str in package.version_set.values_list('number', flat=True):
        v = versioner(v_str)
        comparable = True
        for elem in v.version:
            if isinstance(elem, str):
                comparable = False
        if comparable:
            versions.append(v)
    if versions:
        return str(sorted(versions)[-1])
    return ''


def normalize_license(license):
    """ Handles when:

        * No license is passed
        * Made up licenses are submitted
        * Official PyPI trove classifier licenses
        * Common abbreviations of licenses

    """
    if license is None:
        return "UNKNOWN"
    if license.strip() in settings.LICENSES:
        return license.strip()
    if len(license.strip()) > 20:
        return "Custom"
    return license.strip()


def prepare_thumbnails(image_path):
    image = Image.open(image_path)
    image_dir, image_filename = split(image_path)
    thumbs_dir = join(image_dir, 'thumbs')
    if not exists(thumbs_dir):
        makedirs(thumbs_dir)

    croped_thumbnail = crop_image(image, settings.PROJECT_IMAGE_THUMBNAIL_RATIO)
    thumbnail_path = join(thumbs_dir, image_filename)

    croped_thumbnail.save(thumbnail_path, quality=settings.PROJECT_IMAGE_THUMBNAIL_QUALITY)
    logger.info("Thumbnail {}".format(thumbnail_path))

    shrinked_thumbnails = [
        croped_thumbnail.resize(thumb_size, Image.ANTIALIAS)
        for thumb_size in settings.PROJECT_IMAGE_THUMBNAIL_SIZES
        if thumb_size[0] < croped_thumbnail.size[0]
    ]

    for thumb in shrinked_thumbnails:
        name, ext = splitext(image_filename)
        thumb_path = join(
            thumbs_dir,
            "{name}_{size}{ext}".format(
                name=name,
                size="x".join(map(str, thumb.size)),
                ext=ext
            )
        )
        logger.info("Thumbnail {}".format(thumb_path))
        thumb.save(thumb_path, quality=settings.PROJECT_IMAGE_THUMBNAIL_QUALITY)


def crop_image(image, ratio):
    ratio_x, ratio_y = ratio
    x, y = image.size

    x_unit = x / float(ratio_x)
    y_unit = y / float(ratio_y)

    if x_unit > y_unit:  # to wide
        new_x = ratio_x * y_unit  # so new_x use more narrow y_unit
        new_y = ratio_y * y_unit

    else:  # to high
        new_x = ratio_x * x_unit
        new_y = ratio_y * x_unit  # so new_y use shorter x_unit

    padding_x = (x - new_x) / 2
    padding_y = (y - new_y) / 2

    box = (padding_x, padding_y, x - padding_x, y - padding_y)
    return image.crop(box)


def download_file(file_url, dest_path, file_name=None):
    if not file_name:
        file_name = generate_unique_file_name()
    file_path = join_path_with_file_name(dest_path, file_name)
    makedirs(dest_path, exist_ok=True)
    urllib.request.urlretrieve(file_url, file_path)
    return file_name


def get_file_maintype_from_url(file_url):
    return urllib.request.urlopen(file_url).info().get_content_maintype()


def get_file_subtype_from_url(file_url):
    return urllib.request.urlopen(file_url).info().get_content_subtype()


def get_image_name(file_type):
    return f"{int(round(time.time()*1000))}.{file_type}"


def generate_unique_file_name():
    return str(uuid.uuid4())


def rename_file(file_dir, old_name, new_name):
    file_path_old = join_path_with_file_name(file_dir, old_name)
    file_path_new = join_path_with_file_name(file_dir, new_name)
    os.rename(file_path_old, file_path_new)
    return file_path_new


def join_path_with_file_name(path, file_name):
    if not path.endswith('/'):
        path += '/'
    return f"{path}{file_name}"


def split_path_for_path_and_name(file_path):
    return file_path.rsplit("/", 1)


def cut_domain_name_from_url(file_url):
    return file_url.split("/", 3)[-1]


def delete_file_from_media(image_path):
    folder_path, image_name = split_path_for_path_and_name(image_path)
    image_name = image_name.split(".")[0]
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.find(image_name) != -1:
                os.remove(join(root, file))

