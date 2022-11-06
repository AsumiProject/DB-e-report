import re

E_REPORT_URL = "https://e-report.neu.edu.cn"
WEBVPN_URL = "https://webvpn.neu.edu.cn"
PASS_URL = "https://pass.neu.edu.cn"

E_REPORT_WEBVPN_URL = WEBVPN_URL + "/https/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809"
PASS_WEBVPN_URL = WEBVPN_URL + "/https/77726476706e69737468656265737421e0f6528f693e6d45300d8db9d6562d"

LOGIN = "/login"
INFO = "/api/profiles/{0}?xingming={1}"  # {0} id, {1} name
CHECK_IN = "/notes/create"
CHECK_IN_API = "/api/notes"
TEMPERATURE = "/inspection/items/{0}/records"

LP_MATCHER = re.compile(r'id="loginForm" action="(.+?)"')
LT_MATCHER = re.compile(r'name="lt" value="(.+?)"')
TOKEN_MATCHER = re.compile(r'name="_token" value="(.+?)"')
NAME_MATCHER = re.compile(r'当前用户：(.+?) <span')
CLASS_MATCHER = re.compile(r'"suoshubanji":"(.+?)"')
DATE_MATCHER = re.compile(r'"created_on":"(.+?)"')
