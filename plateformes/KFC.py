from Driver import Driver
from tools import *
from bdd import *
import subprocess

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
            self.proxy = app.proxy
            self.driver = app.driver
    
    def add_cookie(self):
        try:
            for cookie in self.cookies["COOKIE"]:
                if cookie["name"] == "_abck":
                    self.request += f'\n$session.Cookies.Add((New-Object System.Net.Cookie("{cookie["name"]}", "{cookie["value"]}", "{cookie["path"]}", "{cookie["domain"]}")))'
            return True
        except Exception as e:
            print_msg(f"{self.app.format_print}Erreur lors de l'ajout des cookies : {e}", "red")
            return False

    def get_cookie(self):
        try:
            # self.driver.get("https://www.kfc.fr/mon-compte/connexion")
            # cookies = self.driver.get_cookies()
            # self.driver.quit()
            # for cookie in cookies:
            #     session.cookies.set(cookie['name'], cookie['value'], domain=".kfc.fr", path=cookie.get('path', '/'))

            # récupéré les cookies depuis la bdd
            while True:
                # self.cookies = get_and_delete_random_cookie("KFC")
                self.cookies = get_cookies("KFC")
                if self.cookies:
                    break
            return True
        except Exception as e:
            print_msg(f"{self.app.format_print}Erreur lors de la récupération des cookies : {e}", "red")
            return False

    def login(self):
        if not self.get_cookie():
            return None, "Impossible de récupérer les cookies"

        try:
            proxy_host, proxy_port = self.proxy.split(":")
            self.request = f"""
            $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
            $session.UserAgent = "{self.cookies["USER_AGENT"]}"
            $session.Proxy = New-Object System.Net.WebProxy("{proxy_host}", {proxy_port})
            """
            if not self.add_cookie():
                return None, "Impossible d'ajouter les cookies"
            self.request +=f"""
            $response = Invoke-WebRequest -UseBasicParsing -Uri "https://www.kfc.fr/api/login" `
            -Method "POST" `
            -WebSession $session `
            -Headers @{{
            "method"="POST"
            "path"="/api/login"
            "scheme"="https"
            "accept"="application/json, text/plain, */*"
            "accept-encoding"="gzip, deflate, br"
            "accept-language"="fr-FR,fr;q=0.9"
            "culturecode"="fr"
            }}`
            -ContentType "application/json" `
            -Body "{{`"email`":`"{self.email}`",`"password`":`"{self.password}`"}}"
            $response.Content
            """
            # print_msg(self.request, "yellow")
            result = subprocess.run(['powershell', '-Command', self.request], capture_output=True, text=True, timeout=5)
            if not result.stderr:
                try:
                    data = json.loads(result.stdout)
                except:
                    return None, f"Impossible de récupérer le token : {result.stdout}"
                self.bearer = data["token"]
                self.bearer = f"Bearer {self.bearer}"
                self.id = data["user"]["id"]
                self.code_point = data["user"]["loyaltyId"]
                return True, None
            elif "Votre email ou votre mot de passe est incorrect." in result.stderr or "401" in result.stderr:
                return False, "Votre email ou votre mot de passe est incorrect."
            else:
                return None, f"Erreur inattendue lors de la connexion : " + ("timed out" if "timed out" in result.stderr else result.stderr)
        except Exception as e:
            e = "timed out after 5 seconds" if "timed out after" in str(e) else e
            return None, f"Erreur lors de la connexion : {e}"

    def get_points(self):
        try:
            if not self.id:
                return False
            proxy_host, proxy_port = self.proxy.split(":")
            self.request = f"""
            $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
            $session.UserAgent = "{self.cookies["USER_AGENT"]}"
            $session.Proxy = New-Object System.Net.WebProxy("{proxy_host}", {proxy_port})
            """
            if not self.add_cookie():
                return None, "Impossible d'ajouter les cookies"
            self.request +=f"""
            $response = Invoke-WebRequest -UseBasicParsing -Uri "https://www.kfc.fr/api/users/{self.id}/loyaltyinfo" `
            -WebSession $session `
            -Headers @{{
            "method"="GET"
            "path"="/api/users/{self.id}/loyaltyinfo"
            "scheme"="https"
            "accept"="application/json, text/plain, */*"
            "accept-encoding"="gzip, deflate, br"
            "accept-language"="fr-FR,fr;q=0.9"
            "authorization"="{self.bearer}"
            "culturecode"="fr"
            }}
            $response.Content
            """
            result = subprocess.run(['powershell', '-Command', self.request], capture_output=True, text=True, timeout=5)
            if not result.stderr:
                try:
                    data = json.loads(result.stdout)
                except:
                    return None, f"Impossible de récupérer les points : {result.stdout}"
                return {"point":int(data["loyaltyPoints"]), "code_point":str(data["loyaltyId"])}, data["id"]
            else:
                return None, f"Erreur inattendue lors de la récupération des points : {result.stderr}"
        except Exception as e:
            print_msg(f"{self.app.format_print}Erreur lors de la récupération des points : {e}", "red")
            return False, None

    def generate_cookie(self, proxys, id_chrome):
        def accept_cookie():
            if self.click_element(By.ID, "onetrust-pc-btn-handler", 2):
                self.click_element(By.CSS_SELECTOR, '[class="ot-switch-nob"]', 2)
                self.click_element(By.CSS_SELECTOR, '[class="save-preference-btn-handler onetrust-close-btn-handler"]', 2)
                time.sleep(1)
        # On récupère un user agent et un proxy
        self.user_agent = UserAgent().random
        self.proxy = random.choice(proxys)["PROXY"]
        if Driver.__init__(self, id_chrome, self.user_agent, proxy=self.proxy, headless=False) == False:
            return False
        self.start_driver()
        count = 0
        f = faker.Faker()
        while True:
            try:
                self.driver.get("https://kfc.fr/")
                self.ResetSession()
                time.sleep(10)
                accept_cookie()
                self.click_element(By.CSS_SELECTOR, 'app-sign-in a', 5)
                time.sleep(10)

                # On envoie une requete aléatoire pour ce connecter

                self.send_keys(By.ID, "email", f.email())
                self.send_keys(By.ID, "password", f.password())
                self.click_element(By.CSS_SELECTOR, '[type="submit"]', 5)

                # récupéré le network
                test = str(self.presence_of_element(By.CSS_SELECTOR, 'app-message-info li', 5, attribut="innerText"))
                if test == "Votre email ou votre mot de passe est incorrect. Veuillez réessayer.":
                    cookies = self.driver.get_cookies()

                    # on converti les cookies en dictionnaire
                    date = datetime.datetime.now()
                    while datetime.datetime.now() < date + datetime.timedelta(seconds=15):
                        cookie = deserialize_from_json(cookies)
                        cookie = serialize_to_json(cookies)
                        if cookie:
                            add_cookie(cookie, "KFC", self.user_agent, self.proxy)
                            break
                    else:
                        print_msg("Le cookie n'a pas été généré", "yellow")
                else:
                    print_msg(f"Le cookie n'a pas été génére : " + test, "yellow")
                    time.sleep(600)

                self.ResetSession()
                if count == 0:
                    raise Exception("Changement de proxy")
                count += 1
            except:
                try:
                    self.driver.quit()
                except:
                    pass
                self.update_user_agent(UserAgent().random)
                self.update_proxy(random.choice(proxys)["PROXY"])
                self.start_driver()
                time.sleep(10)
                pass