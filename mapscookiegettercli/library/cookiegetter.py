#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: cookiegetter.py
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
Main code for cookiegetter

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
import sys
import pickle
from pathlib import Path
from time import sleep

from requests import Session
from selenium.common.exceptions import NoSuchWindowException

from mapscookiegettercli.mapscookiegettercliexceptions import UnsupportedOS, UnsupportedDefaultBrowser
from mapscookiegettercli.browsers import Chrome, Firefox, IE, Edge

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''04-03-2019'''
__copyright__ = '''Copyright 2019, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''cookiegetter'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())

MAPS_LOGIN = ('https://accounts.google.com/signin/v2/identifier?'
              'hl=en&'
              'passive=true&'
              'continue=https%3A%2F%2Fwww.google.com%2Fmaps%2F%4040.7484986%2C-73.9857129%2C15z&'
              'service=local&'
              'flowName=GlifWebSignIn&'
              'flowEntry=ServiceLogin')

LOGGED_IN_HEURISTIC = 'See travel times, traffic and nearby places'


class CookieGetter:  # pylint: disable=too-few-public-methods
    """Object able to retrieve the cookies from an interactive login session to a google maps service"""

    def __init__(self):
        logger_name = u'{base}.{suffix}'.format(base=LOGGER_BASENAME,
                                                suffix=self.__class__.__name__)
        self._logger = logging.getLogger(logger_name)
        self.os = self._identify_os()  # pylint: disable=invalid-name
        self._logger.info('Identified OS as %s', self.os)
        self.default_browser = self._identify_default_browser(self.os)
        self._logger.info('Identified default browser as %s', self.default_browser)

    @staticmethod
    def _identify_os():
        platforms = {
            'linux': 'linux',
            'linux1': 'linux',
            'linux2': 'linux',
            'darwin': 'mac',
            'win32': 'windows'
        }
        platform = sys.platform
        if platform not in platforms:
            raise UnsupportedOS(platform)
        return platforms.get(platform)

    def _identify_default_browser(self, identified_os):
        browser = getattr(self, '_identify_browser_{os}'.format(os=identified_os))()
        if browser == 'unknown':
            raise UnsupportedDefaultBrowser
        return browser

    @staticmethod
    def _identify_browser_mac():
        from plistlib import load, FMT_BINARY  # pylint: disable=no-name-in-module
        supported_browsers = ('firefox', 'chrome')
        default_browser_plist_path = ('~/Library/Preferences/com.apple.LaunchServices/'
                                      'com.apple.launchservices.secure.plist')
        path = Path(default_browser_plist_path).expanduser()
        with open(path, 'rb') as plist:
            settings = load(plist, fmt=FMT_BINARY)
        browser_setting = next((setting.get('LSHandlerRoleAll') for setting in settings.get('LSHandlers')
                                if setting.get('LSHandlerContentType') == 'public.html'),
                               'Unknown')
        browser = next((browser for browser in supported_browsers
                        if browser in browser_setting.lower()),
                       'unknown')
        return browser

    @staticmethod
    def _identify_browser_windows():
        from winreg import HKEY_CURRENT_USER, HKEY_CLASSES_ROOT, OpenKey, QueryValueEx  # pylint: disable=import-error
        supported_browsers = ('firefox', 'chrome', 'edge', 'ie')
        default_browser_registry_path = (r'Software\Microsoft\Windows\Shell\Associations'
                                         r'\UrlAssociations\https\UserChoice')
        with OpenKey(HKEY_CURRENT_USER, default_browser_registry_path) as key:
            program_id = QueryValueEx(key, 'ProgId')[0]
        browser = next((browser for browser in supported_browsers
                        if browser in program_id.lower()),
                       None)
        if browser:
            return browser
        with OpenKey(HKEY_CLASSES_ROOT, f'{program_id}\\Application') as key:
            application_name = QueryValueEx(key, 'ApplicationName')[0]
        browser = next((browser for browser in supported_browsers
                        if browser in application_name.lower()),
                       'unknown')
        return browser

    @staticmethod
    def _identify_browser_linux():
        from subprocess import Popen, PIPE
        supported_browsers = ('firefox', 'chrome')
        command = ['xdg-settings', 'get', 'default-web-browser']
        try:
            get_browser_command = Popen(command, stdout=PIPE, stderr=PIPE)
        except FileNotFoundError:
            print('Could not execute xdg-settings, probably unsupported version of linux.')
            return 'unknown'
        output, _ = get_browser_command.communicate()
        browser = next((browser for browser in supported_browsers
                        if browser in output.decode('utf-8')),
                       'unknown')
        return browser

    def _get_driver(self):
        browsers = {'chrome': Chrome,
                    'firefox': Firefox,
                    'ie': IE,
                    'edge': Edge}
        return browsers.get(self.default_browser)()

    def run(self, cookie_file_name='location_sharing.cookies'):
        """Executes the process and saves the cookies

        Args:
            cookie_file_name (str): The path and name of the exported cookie file

        Returns:

        """
        driver = self._get_driver()
        self._logger.info('Starting interactive login process.')
        try:
            driver.get(MAPS_LOGIN)
            while LOGGED_IN_HEURISTIC not in driver.page_source:
                sleep(0.5)
            session = self._get_session(driver)
            self._save_cookies(session, cookie_file_name)
            self._logger.info('Terminating browser session.')
            driver.close()
            driver.quit()
        except NoSuchWindowException:
            self._logger.warning('Window disappeared, seems like it was closed manually')

    def _get_session(self, driver):
        self._logger.info('Log in successful, getting session cookies.')
        session = Session()
        self._logger.info('Transferring cookies to a requests session.')
        for cookie in driver.get_cookies():
            for invalid in ['httpOnly', 'expiry']:
                try:
                    del cookie[invalid]
                except KeyError:
                    pass
            session.cookies.set(**cookie)
        return session

    def _save_cookies(self, session, file_name):
        self._logger.info('Saving the requests session to pickled file "%s".', file_name)
        with open(file_name, 'wb') as ofile:
            pickle.dump(session.cookies, ofile)
