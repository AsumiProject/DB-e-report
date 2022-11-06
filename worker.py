import ssl
import sys
import time
from random import randint
from datetime import datetime, timedelta, timezone

from aiohttp import ClientSession, ClientTimeout
from constants import *


class Worker:
    _header = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Pixel 6 Build/SD1A.210817.023; wv) AppleWebKit/537.36 (KHTML, '
                      'like Gecko) Version/4.0 Chrome/94.0.4606.71 Mobile Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    _session = None
    _sslcontext = ssl.create_default_context(cafile="resources/neu-edu-cn-chain.pem")
    _timeout = ClientTimeout(total=10)
    _token = ""
    _name = ""
    _class = ""
    _date = ""
    _pass_url = PASS_URL

    def __init__(self,
                 userid: str,
                 password: str,
                 ip: str = "",
                 no_error: bool = False,
                 use_webvpn: bool = False,
                 debug: bool = False,
                 ):
        """
        :param userid: student id
        :param password: password
        :param ip: ip address for "X-Forwarded-For" header
        :param no_error: If true, print error message and exit with code 0 when error occurs. If you don't want to be
        disturbed by GitHub's email, set it to True.
        :param use_webvpn: If true, will use webvpn to bypass ip restriction.
        :param debug: If true, will print debug message. Don't use it in public repository.
        """
        self._userid = userid
        self._password = password
        self._ip = ip
        self._no_error = no_error
        self._use_webvpn = use_webvpn
        self._debug = debug

        if ip:
            self._header['X-Forwarded-For'] = ip
        if self._use_webvpn:
            self._login_url = WEBVPN_URL + LOGIN
            self._feedback_url = WEBVPN_URL
            self._info = E_REPORT_WEBVPN_URL + INFO
            self._check_in = E_REPORT_WEBVPN_URL + CHECK_IN
            self._check_in_api = E_REPORT_WEBVPN_URL + CHECK_IN_API
            self._temperature = E_REPORT_WEBVPN_URL + TEMPERATURE
        else:
            self._login_url = E_REPORT_URL + LOGIN
            self._feedback_url = E_REPORT_URL
            self._info = E_REPORT_URL + INFO
            self._check_in = E_REPORT_URL + CHECK_IN
            self._check_in_api = E_REPORT_URL + CHECK_IN_API
            self._temperature = E_REPORT_URL + TEMPERATURE

    async def _login(self, skip_webvpn: bool = False):
        try:
            if not skip_webvpn:
                self._session = ClientSession(headers=self._header, timeout=self._timeout)
            resp = await self._session.get(self._login_url, ssl=self._sslcontext)
            if resp.status != 200:
                raise ConnectionError(f"Server Connection Error: {resp.status}\n"
                                      f"{await resp.text() if self._debug else ''}")

            text = await resp.text()
            lt = LT_MATCHER.findall(text)
            lp = LP_MATCHER.findall(text)

            if len(lt) < 1 or len(lp) < 1:
                raise RuntimeError(f"Unexpected Server Response: {resp.status}\n"
                                   f"{text if self._debug else ''}")

            lt, lp = lt[0], lp[0]
            resp = await self._session.post(self._pass_url + lp, data={
                "rsa": self._userid + self._password + lt,
                "ul": len(self._userid),
                "pl": len(self._password),
                "lt": lt,
                "execution": "e1s1",
                "_eventId": "submit",
            }, ssl=self._sslcontext)
            if resp.host != self._feedback_url.removeprefix("https://"):
                raise RuntimeError(f"Auth Failed: {resp.status}\n"
                                   + (await resp.text()) if self._debug else "Please check your username and password.")

            if self._use_webvpn and not skip_webvpn:
                self._login_url = E_REPORT_WEBVPN_URL + LOGIN
                self._feedback_url = WEBVPN_URL
                self._pass_url = WEBVPN_URL  # the returned "lp" already includes webvpn path...
                await self._login(skip_webvpn=True)
        except Exception as e:
            await self._session.close()
            if self._no_error:
                print("Login Failed: " + str(e))
                sys.exit(0)
            raise

    async def _get_token(self):
        try:
            resp = await self._session.get(self._check_in, ssl=self._sslcontext)
            text = await resp.text()
            self._token = TOKEN_MATCHER.findall(text)[0]
            self._name = NAME_MATCHER.findall(text)[0]
        except Exception as e:
            await self._session.close()
            if self._no_error:
                print("Get Token Failed: " + str(e))
                sys.exit(0)
            raise

    async def _get_info(self):
        try:
            resp = await self._session.get(self._info.format(self._userid, self._name), ssl=self._sslcontext)
            text = await resp.text()
            self._class = CLASS_MATCHER.findall(text)[0].replace('\\\\', '\\').encode('utf-8').decode(
                'unicode-escape')  # fix encoding error
            self._date = DATE_MATCHER.findall(text)[0]
        except Exception as e:
            await self._session.close()
            if self._no_error:
                print("Get Info Failed: " + str(e))
                sys.exit(0)
            raise

    async def _do_check_in(self) -> bool:
        if self._date == time.strftime(r'%Y-%m-%d', datetime.now(timezone(timedelta(hours=8))).timetuple()):
            return False
        try:
            resp = await self._session.post(self._check_in_api,
                                            data={
                                                "_token": self._token,
                                                "jibenxinxi_shifoubenrenshangbao": 1,
                                                "profile[xuegonghao]": self._userid,
                                                "profile[suoshubanji]": self._class,
                                                "jiankangxinxi_muqianshentizhuangkuang": "正常",
                                                "xingchengxinxi_weizhishifouyoubianhua": 0,
                                                "qitashixiang_qitaxuyaoshuomingdeshixiang": None
                                            }, ssl=self._sslcontext)
            if resp.status != 201:
                raise RuntimeError(f"Unexpected Server Response: {resp.status}\n"
                                   f"{await resp.text() if self._debug else ''}")
            return True
        except Exception as e:
            await self._session.close()
            if self._no_error:
                print("Check In Failed: " + str(e))
                sys.exit(0)
            raise

    async def _report_temperature(self):
        try:
            resp = await self._session.post(self._temperature.format(self._temperature_id), data={
                "_token": self._token,
                "temperature": 36 + randint(4, 7) / 10,
                "suspicious_respiratory_symptoms": 0,
                "symptom_descriptions": None
            }, ssl=self._sslcontext)
            if resp.status != 200:
                raise RuntimeError(f"Unexpected Server Response: {resp.status}\n"
                                   f"{await resp.text() if self._debug else ''}")
        except Exception as e:
            await self._session.close()
            if self._no_error:
                print("Report Temperature Failed: " + str(e))
                sys.exit(0)
            raise

    @property
    def _temperature_id(self):
        now = datetime.now(timezone(timedelta(hours=8))).hour
        return 1 if now < 10 else 2 if now < 16 else 3

    async def run(self):
        print("Logging in...")
        await self._login()
        print("Getting token...")
        await self._get_token()
        print("Getting info...")
        await self._get_info()
        print("Checking in...")
        if await self._do_check_in():
            print("Check in success!")
        else:
            print("Already checked in!")
        print("Reporting body temperature...")
        await self._report_temperature()
        print("Report body temperature success!")
        await self._session.close()
        print("Done!")
