from Driver import Driver
from tools import *
from bdd import *
import requests

class KFC(Driver):
    def __init__(self, app =None):
        if app:
            self.cookies = {
                "ID": None,
                "PLATEFORME": "KFC",
                "COOKIE": None,
            }
            self.app = app
            self.email = app.email
            self.password = app.password
            self.user_agent = app.user_agent
            self.proxy = app.proxy
            self.driver = app.driver
            self.user_agent = app.user_agent

    def create_session(self):
            self.session = requests.Session()
            self.session.headers.update({
                "authority": "www.kfc.fr",
                "User-Agent": self.user_agent,
                "scheme":"https",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Dnt": "1",
                "Referer": "https://www.kfc.fr/programme-fidelite-colonel-club-server",
                "Sec-Ch-Ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \";Not?A_Brand\";v=\"24\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Windows\"",
                "Sec-Fetch-Dest": "script",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-origin",
            })
            if self.proxy:
                self.proxies = {
                    "http": f"http://{self.proxy}",
                }
                self.session.proxies.update(self.proxies)

    def get_cookie(self):
        try:
            # Récupéré les cookies via requests
            # session = self.session
            # response = session.get("https://api.kfc.fr/configurations")
            # self.session.cookies.update(response.cookies)
            # return True


            # Récupéré les cookies via selenium
            # self.driver.get("https://www.kfc.fr/mon-compte/connexion")
            # cookies = self.driver.get_cookies()
            # self.driver.quit()
            # for cookie in cookies:
            #     session.cookies.set(cookie['name'], cookie['value'], domain=".kfc.fr", path=cookie.get('path', '/'))

            # récupéré les cookies depuis la bdd
            while True:
                self.cookies = get_cookies("KFC")
                if self.cookies:
                    break
            # ajouter chaque cookie dans la session
            self.user_agent = self.cookies["USER_AGENT"]
            self.proxy = self.cookies["PROXY"]
            self.create_session()
            for cookie in self.cookies["COOKIE"]:
                self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])

            return True
        except Exception as e:
            print_msg(f"Erreur lors de la récupération des cookies : {e}", "red")
            return False

    def login(self):
        if not self.get_cookie():
            return None, "Impossible de récupérer les cookies"

        count = 0
        while True:
            try:
                # response = self.session.post("http://ip.jsontest.com/", json={"email": self.email, "password": self.password}, timeout=10, proxies=self.proxies)
                response = self.session.post("https://www.kfc.fr/api/login", json={"email": self.email, "password": self.password}, timeout=10, proxies=self.proxies)
                if response.status_code == 200:
                    data = response.json()
                    self.bearer = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.bearer}"})
                    self.id = data["user"]["id"]
                    self.code_point = data["user"]["loyaltyId"]
                    return True, None
                elif response.status_code == 401:
                    msg = response.json().get("errors", [response.text])[0]
                    return False, msg
                else:
                    return None, f"Erreur inattendue lors de la connexion : {response.status_code} {response.text}"
            except Exception as e:
                if count !=  6:
                    delete_cookie(self.cookies["ID"])
                    self.proxy = random.choice(self.app.all_proxys)["PROXY"]
                    self.create_session()
                    self.get_cookie()
                    count += 1
                    continue
                else:
                    return None, f"Erreur lors de la connexion : {e}"

    def get_points(self):
        try:
            if not self.id:
                return False
            response = self.session.get(f"https://www.kfc.fr/api/users/{self.id}/loyaltyinfo")
            if response.status_code == 200:
                data = response.json()
                return data["loyaltyPoints"]
            else:
                print_msg(f"Erreur inattendue : {response.status_code} {response.text}", "red")
                return False
        except Exception as e:
            print_msg(f"Erreur lors de la récupération des points : {e}", "red")
            return False

    def generate_cookie(self, user_agents, proxys):
        def accept_cookie():
            if self.click_element(By.ID, "onetrust-pc-btn-handler", 2):
                self.click_element(By.CSS_SELECTOR, '[class="ot-switch-nob"]', 2)
                self.click_element(By.CSS_SELECTOR, '[class="save-preference-btn-handler onetrust-close-btn-handler"]', 2)
                time.sleep(1)
        # On récupère un user agent et un proxy
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        self.proxy = random.choice(proxys)["PROXY"]
        if Driver.__init__(self, self.user_agent, proxy=self.proxy, headless=True) == False:
            return False
        self.start_driver()
        self.driver.get("https://www.kfc.fr/mon-compte/connexion")
        self.presence_of_element(By.CSS_SELECTOR, "app-login-section", 120)
        accept_cookie()
        count = 0
        while True:
            try:
                # récupérer les cookies
                cookies = self.driver.get_cookies()
                # on converti les cookies en dictionnaire
                add_cookie(serialize_to_json(cookies), "KFC", self.user_agent, self.proxy)
                # self.ResetSession()
                # self.presence_of_element(By.CSS_SELECTOR, "app-login-section", 120)
                # accept_cookie()
                # time.sleep(2)
                if count == 0:
                    raise Exception("Changement de proxy")
                count += 1
            except:
                try:
                    self.driver.quit()
                except:
                    pass
                self.update_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
                self.update_proxy(random.choice(proxys)["PROXY"])
                self.start_driver()
                time.sleep(3)
                self.change_page("https://www.kfc.fr/mon-compte/connexion")
                accept_cookie()
                pass