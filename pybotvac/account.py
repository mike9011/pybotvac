import binascii
import os
import requests

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from .robot import Robot


class Account:
    """
    Class containing data and methods for interacting with a pybotvac cloud session.

    :param email: Email for pybotvac account
    :param password: Password for pybotvac account
    """
    ENDPOINT = 'https://beehive.neatocloud.com/'

    def __init__(self, email, password):
        self._robots = set()
        self._headers = {'Accept': 'application/vnd.neato.nucleo.v1'}
        self._login(email, password)

    def _login(self, email, password):
        """
        Login to pybotvac account using provided email and password
        :param email: email for pybotvac account
        :param password: Password for pybotvac account
        :return:
        """
        response = requests.post(urljoin(self.ENDPOINT, 'sessions'),
                             json={'email': email,
                                   'password': password,
                                   'platform': 'ios',
                                   'token': binascii.hexlify(os.urandom(64)).decode('utf8')},
                             headers=self._headers)

        response.raise_for_status()
        access_token = response.json()['access_token']

        self._headers['Authorization'] = 'Token token=%s' % access_token

    @property
    def robots(self):
        """
        Return set of robots for logged in account.
        :return:
        """
        if not self._robots:
            self.refresh()

        return self._robots

    def refresh(self):
        """
        Get information about robots connected to account.
        :return:
        """
        resp = requests.get(urljoin(self.ENDPOINT, 'dashboard'), headers=self._headers)
        resp.raise_for_status()

        for robot in resp.json()['robots']:
            self._robots.add(Robot(name=robot['name'],
                                   serial=robot['serial'],
                                   secret=robot['secret_key']))

