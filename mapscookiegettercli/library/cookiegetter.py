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

import webdriver_manager

from mapscookiegettercli.mapscookiegettercliexceptions import UnsupportedOS, UnsupportedDefaultBrowser

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


class CookieGetter:
    """Object able to retrieve the cookies from an interactive login session to a google maps service"""

    def __init__(self):
        logger_name = u'{base}.{suffix}'.format(base=LOGGER_BASENAME,
                                                suffix=self.__class__.__name__)
        self._logger = logging.getLogger(logger_name)
        self.os = self._identify_os()
        self.default_browser = self._identify_default_browser(self.os)
        self.drivers_path = Path(__file__).parent.joinpath('..' '/drivers')

    @staticmethod
    def _identify_os():
        platforms = {
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
        from plistlib import load, FMT_BINARY
        supported_browsers = ('firefox', 'safari', 'chrome', 'opera')
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
        from winreg import HKEY_CURRENT_USER, HKEY_CLASSES_ROOT, OpenKey, QueryValueEx
        supported_browsers = ('firefox', 'safari', 'chrome', 'opera', 'edge', 'ie')
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
        supported_browsers = ('firefox', 'chrome', 'chromium', 'opera', 'firefox')
        command = ['xdg-settingsa', 'get', 'default-web-browser']
        try:
            get_browser_command = Popen(command, stdout=PIPE, stderr=PIPE)
        except FileNotFoundError:
            print('Could not execute xdg-settings, propably unsupported version of linux.')
            return 'unknown'
        output, error = get_browser_command.communicate()
        browser = next((browser for browser in supported_browsers
                        if browser in output.decode('utf-8')),
                       'unknown')
        return browser

    def run(self):
        self._bootstrap_browser()
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        versions = webdriver_manager.versions(self.drivers_path, [self.default_browser])
        driver_name = versions['chromedriver'][0][1]
        path_to_chromedriver = Path(self.drivers_path) / driver_name

        chrome_options = Options()
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--profile-directory=Default')
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--disable-plugins-discovery')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-infobars')
        driver = webdriver.Chrome(executable_path=path_to_chromedriver, chrome_options=chrome_options)
        driver.delete_all_cookies()
        login_url = 'https://accounts.google.com/signin/v2/identifier?hl=en&passive=true&continue=https%3A%2F%2Fwww.google.com%2Fmaps%2F%4052.3499986%2C4.9115129%2C15z&service=local&flowName=GlifWebSignIn&flowEntry=ServiceLogin'
        driver.get(login_url)
        return driver

    def _bootstrap_browser(self):
        webdriver_manager.update(self.default_browser, self.drivers_path)

    def save_cookies(self, driver, cookie_file_name='location_sharing.cookies'):
        if 'id="nearby-suggestions"' in driver.page_source:
            from requests import Session
            session = Session()
            for cookie in driver.get_cookies():
                for invalid in ['httpOnly', 'expiry']:
                    try:
                        del cookie[invalid]
                    except:
                        pass
                session.cookies.set(**cookie)
                with open(cookie_file_name, 'wb') as f:
                    pickle.dump(session.cookies, f)
            driver.close()
