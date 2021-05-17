#
# Copyright (C) 2021 Satoru SATOH <satoru.satoh@gmail.com>
# SPDX-License-Identifier: MIT
#
r"""Utility functions to list and find appropriate parser class objects and
instances.

.. versionchanged:: 0.10.2

   - Split and re-organize the module and export only some functions.

.. versionadded:: 0.9.5

   - Add to abstract processors such like Parsers (loaders and dumpers).
"""
from .detectors import (
    is_iterable, is_path, is_path_obj, is_file_stream, is_ioinfo,
    is_stream_ioinfo, is_path_like_object, is_paths,
    is_dict_like, is_list_like
)
from .files import (
    get_file_extension, get_path_from_stream, expand_paths, are_same_file_types
)
from .lists import (
    groupby, concat
)
from .utils import (
    filter_options, noop
)


__all__ = [
    'is_iterable', 'is_path', 'is_path_obj', 'is_file_stream', 'is_ioinfo',
    'is_stream_ioinfo', 'is_path_like_object', 'is_paths',
    'is_dict_like', 'is_list_like',
    'get_file_extension', 'get_path_from_stream', 'expand_paths',
    'are_same_file_types',
    'groupby', 'concat',
    'filter_options', 'noop',
]

# vim:sw=4:ts=4:et: