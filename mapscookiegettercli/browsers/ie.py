#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: ie.py
#
# Copyright 2019 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
ie package

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html
"""

import logging


from webdriver_manager.microsoft import IEDriverManager
from selenium import webdriver

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''04-03-2019'''
__copyright__ = '''Copyright 2019, Costas Tyfoxylos'''
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''internet_explorer'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class IE:  # pylint: disable=too-few-public-methods
    """Bootstraps an internet explorer selenium driver with the required settings"""

    def __new__(cls):
        logger_name = u'{base}.{suffix}'.format(base=LOGGER_BASENAME,
                                                suffix='bootstrapper')
        logger = logging.getLogger(logger_name)
        logger.info('Starting up internet explorer driven by selenium')
        driver = webdriver.Ie(executable_path=IEDriverManager().install())
        logger.info('Deleting all cookies')
        driver.delete_all_cookies()
        logger.info('Returning driver')
        return driver
