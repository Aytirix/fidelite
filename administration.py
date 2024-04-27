from plateformes.KFC import *
from Driver import Driver
from bdd import *

class administration(threading.Thread, Driver):
    def __init__(self, num, id, email, password, plateformes, proxy, force_check=False):
        threading.Thread.__init__(self)
        self.num = num
        self.email = email
        self.password = password
        self.plateformes = plateformes
        self.proxy = proxy

        self.id = id if id else get_id_compte_email_password(email, password)
        self.force_check = force_check
        self.asso_compte_plateforme = None
        if not self.id:
            self.id = add_comptes(email, password)
            if not self.id:
                print_msg(f"Impossible d'ajouter le compte {email} dans la base de données", "red")
                self.stop_programme(stop=True)
                return False
        else:
            self.asso_compte_plateforme = check_asso_compte_plateforme(self.email, password)
            if self.asso_compte_plateforme:
                self.id = self.asso_compte_plateforme[0]["ID_COMPTE"]

        if Driver.__init__(self, None, proxy=self.proxy, headless=True) == False:
            return False
        
    def liaison_plateforme(self):
        try:
            # Charger dynamiquement le module de la plateforme
            platform_module = importlib.import_module(f"plateformes.{self.plateforme}")

            # Récupérer la classe de la plateforme à partir du module
            platform_class = getattr(platform_module, self.plateforme)

            # Instancier la classe de la plateforme
            self.app = platform_class(self)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Plateforme non prise en charge : {self.plateforme}") from e

    def stop_programme(self):
        """
        Cette fonction permet d'arrêter le programme
        """
        try:
            self.driver.quit()
        except:
            pass
        sys.exit()

    def error_screen(self, add_erreur):
        """
        Cette fonction permet de gérer les erreurs qui peuvent se produire lors de l'utilisation du driver
        Si une erreur se produit on essaye de relancer le programme
        # param add_erreur : permet d'ajouter un message d'erreur dans la base de données
        """
        try:
            # Vérifier si la page est ouverte
            if "La fenêtre a été fermée" in str(add_erreur):
                self.stop_programme(stop=True)
        except Exception as e:
            print_msg(f"{self.format_print}Erreur inattendue lors de la gestion des erreurs : {e}", "red")
            pass
    
    def connexion(self, acp):
        """
        Cette fonction permet de se connecter à la plateforme avec les identifiants

        Retour :
            Si aucune erreur ne se produit :
                driver : driver
                None : message d'erreur
            Si une erreur se produit :
                driver : driver
                error : message d'erreur
        """
        # On essaye de se connecter avec l'email et le mot de passe
        status = None
        points = None
        code_point = None
        login, err = self.app.login()
        if login == True:
            status = 1
            test_point, err = self.app.get_points()
            # Si c'est pas un dictionaire ou qu'il n'y a pas 2 clés on considère que c'est une erreur
            if not test_point and not isinstance(test_point, dict):
                print_msg(f"{self.format_print}Impossible de récupérer les points", "red")
            elif isinstance(test_point, dict) and len(test_point) == 2:
                points = test_point["point"]
                code_point = test_point["code_point"]
            else:
                # delete_cookie(self.app.cookies["ID"])
                print_msg(f"{self.format_print}Impossible de récupérer les points : {err}", "red")

        elif login == False:
            status = 0
            print_msg(f"{self.format_print}Impossible de se connecter : {err}", "red")
        else:
            # delete_cookie(self.app.cookies["ID"])
            print_msg(f"{self.format_print}Erreur inattendue lors de la connexion : {err}", "red")
        
        if self.plateforme in str(self.asso_compte_plateforme):
            if acp and (acp["ACTIF"] != status or acp["POINT"] != points):
                if update_asso_compte_plateforme(self.id, self.plateforme, status, points, code_point, err):
                    print_msg(f"{self.format_print}Mise à jour d'un compte status : {status} points : {acp['POINT']} -> {points}", "green" if status else "red") if status == 1 else None
        else:
            update_last_check_proxy(self.proxy, datetime.datetime.now()+datetime.timedelta(minutes=5))
            if add_asso_compte_plateforme(self.id, self.plateforme, status, points, code_point, err):
                print_msg(f"{self.format_print}Ajout d'un compte status : {status} points : {points}", "green" if status else "red") if status == 1 else None
        return True

    def run(self):
        try:
            for plateforme in self.plateformes:
                self.plateforme = plateforme["NOM"]
                self.format_print = f"[{self.num}] | [{self.plateforme}] {self.email} | "
                if self.asso_compte_plateforme:
                    for acp in self.asso_compte_plateforme:
                            if acp["NOM_PLATEFORME"] != self.plateforme:
                                continue
                            if acp["ACTIF"] == "0":
                                continue
                            # Si il a été vérifier depuis moins d'une semaine on l'ignore
                            if acp["LAST_CHECK"] != None and (datetime.datetime.now() - acp["LAST_CHECK"]).days < 3 and not self.force_check and acp["ACTIF"] != None and acp["POINT"] != None:
                                    break
                            self.liaison_plateforme()
                            self.connexion(acp)
                            break
                    else:
                        self.liaison_plateforme()
                        self.connexion(None)
                else:
                    self.liaison_plateforme()
                    self.connexion(None)
        except Exception as e:
            print_msg(f"{self.format_print}Erreur inattendue lors de l'exécution du programme : {e}", "red")
            pass
        self.stop_programme()