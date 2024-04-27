from SeleniumV2 import SeleniumV2
from tools import *

class Driver(SeleniumV2):
    def __init__(self, id_chrome, DeZoom=False, proxy=False, headless=False, performance = False):
        super().__init__()
        SeleniumV2.__init__(self)
        self.options = webdriver.ChromeOptions()
        self.capabilities = DesiredCapabilities.CHROME.copy()
        self.service = webdriver.chrome.service.Service("chromedriver.exe")
        self.driver = None

        # DEZOOM
        if DeZoom:
            self.options.add_argument("--force-device-scale-factor=0.3")

        # PERFORMANCE
        if performance:
            self.capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

        # PROXY
        self.update_proxy(proxy)
        
        # HEADLESS
        if headless:
            self.options.add_argument("--headless=new")
        else:
            self.options.add_argument("--start-maximized")

        self.update_user_agent(UserAgent().random)

        # Pour mettre l'id du compte comme nom de profil
        # Si id existe, on l'utilise pour le nom du profil
        try:
            # si profile_path qui est dans le .env existe et qu'il n'est pas vide
            data_dir = os.getenv("profile_path")
            if id_chrome == 0 or id_chrome and data_dir:
                testid_dir = os.path.join(data_dir,"!fidelite", str(id_chrome))
            else:
                while True:
                    testid_dir = os.path.join(data_dir,"!fidelite", "default", str(random.randint(0, 99999)))
                    if not os.path.exists(testid_dir):
                        break

            self.options.add_argument(f"--user-data-dir={testid_dir}")
        except:
            pass

        # AUTRES
        # désactiver les messages d'erreurs
        self.options.add_argument("--disable-logging")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--mute-audio")
        self.options.add_argument("disable-infobars")
        # disabling infobars
        self.options.add_argument("--disable-extensions")
        # disabling extensions
        self.options.add_argument("--disable-gpu")
        # applicable to windows os only
        self.options.add_argument("--disable-dev-shm-usage")
        # overcome limited resource problems
        self.options.add_argument("--no-sandbox")
        # Bypass OS security model
        self.options.add_argument("-disable-accelerated-2d-canvas")
        # Disable hardware acceleration
        self.options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )  # pour ne pas être détecté par le site
        self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.options.add_argument("--log-level=3")
        self.capabilities["acceptSslCerts"] = True  # Accepte tous les certificats SSL.

    def update_proxy(self, proxy):
        try:
            if proxy:
                ip, port = proxy.split(":")
                self.options.add_argument("--proxy-server={}:{}".format(ip, port))
        except:
            print_msg("Erreur lors de l'ajout du proxy dans le driver : " + str(proxy), "red")
            pass

    def update_user_agent(self, user_agent):
        self.options.add_argument(f"user-agent={user_agent}")

    def start_driver(self):
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options, desired_capabilities=self.capabilities)
        except Exception as e:
            if self.driver is not None:
                self.driver.quit()
            print_msg("Erreur lors du lancement du driver : " + str(e), "red")
            return False

        try:
            self.driver.set_page_load_timeout(180)
        except Exception as e:
            try:
                self.driver.quit()
            except:
                pass
            self.print_msg("Erreur de chargement de la page" + str(e), "red")
