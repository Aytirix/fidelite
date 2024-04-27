from Driver import Driver
from tools import *

class KFC(Driver):
    def __init__(self, app):
        self.email = app.email
        self.password = app.password
        self.user_agent = app.user_agent
        self.proxy = app.proxy
        self.driver = app.driver
        self.session = requests.Session()
        self.session.headers.update({
            "authority": "api.kfc.fr",
            "User-Agent": self.user_agent,
            "scheme":"https",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "Origin": "https://www.kfc.fr",
            "Dnt": "1",
            "Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Chromium\";v=\"119\", \";Not A Brand\";v=\"24\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "culturecode":"fr"
        })
        if self.proxy:
            # Séparation de l'adresse IP et du port
            proxy_ip, proxy_port = self.proxy.split(":")

            # Mise à jour de la session avec les informations de proxy
            proxies = {
                "http": f"http://{proxy_ip}:{proxy_port}",
            }
            self.session.proxies = proxies

    def get_cookie(self):
        try:
            self.driver.get("https://www.kfc.fr/mon-compte/connexion")

            # récupéré tout les cookies
            cookies = self.driver.get_cookies()
            # fermer le driver
            self.driver.quit()
            abck_cookie = None
            ak_bmsc_cookie = None
            bm_sz_cookie = None
            for cookie in cookies:
                if cookie['name'] == '_abck':
                    abck_cookie = cookie['value']
                elif cookie['name'] == 'ak_bmsc':
                    ak_bmsc_cookie = cookie['value']
                elif cookie['name'] == 'bm_sz':
                    bm_sz_cookie = cookie['value']

            if not abck_cookie:
                return False
            
            if not ak_bmsc_cookie:
                return False
            
            if not bm_sz_cookie:
                return False

            self.session.cookies.set('_abck', abck_cookie, domain='.kfc.fr', path='/')
            self.session.cookies.set('ak_bmsc', ak_bmsc_cookie, domain='.www.kfc.fr', path='/')
            self.session.cookies.set('bm_sz', bm_sz_cookie, domain='.kfc.fr', path='/')
            return True
        except Exception as e:
            print_msg(f"Erreur lors de la connexion : {e}", "red")
            return False

    def login(self):
        try:
            if not self.get_cookie():
                return None, "Impossible de récupérer les cookies"
            
            response = self.session.post("https://www.monip.org/", json={"email": self.email, "password": self.password})
            if response.status_code == 200:
                data = response.json()
                self.bearer = data["token"]
                self.session.headers.update({"Authorization": f"Bearer {self.bearer}"})
                self.id = data["user"]["id"]
                self.code_point = data["user"]["loyaltyId"]
                return True, None
            elif response.status_code == 401:
                try:
                    msg = response.json()["errors"][0]
                except:
                    msg = response.text
                return False, msg
            else:
                return None, f"Erreur inattendue lors de la connexion : {response.status_code} {response.text}"
        except Exception as e:
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