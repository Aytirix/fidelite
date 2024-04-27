from tools import *

class DELARTE():
    def __init__(self, session):
        self.points = None
        self.session = session

    def Connexion(self):

        try:
            self.session.change_page("https://www.kfc.fr/mon-compte/connexion")

            self.AcceptCookies()

            if not self.session.send_keys(by=By.ID, value="email", keys=self.session.email, timeout=5, msg=True):
                return None, "Erreur lors de la saisie de l'email"
            
            if not self.session.send_keys(by=By.ID, value="password", keys=self.session.password, timeout=5, msg=True):
                return None, "Erreur lors de la saisie du mot de passe"
            
            if not self.session.click_element(by=By.CSS_SELECTOR, value="button[type='submit']", timeout=5, msg=True):
                return None, "Erreur lors du clic sur le bouton de connexion"

            return True, None
        except Exception as e:
            return None, f"Erreur inattendue lors de la connexion : {e}"

    def verif_connect(self):
        if self.session.presence_of_element(by=By.CSS_SELECTOR, value="span.pts", timeout=5, msg=False):
            return True, None
        return False, None
        
    def AcceptCookies(self):
        self.session.click_element(by=By.ID, value="onetrust-accept-btn-handler", timeout=3, wait=5)

    def get_points(self):
        points = self.session.presence_of_element(by=By.CSS_SELECTOR, value='[class="points"]', timeout=5, msg=True, attribut="innerText")
        if points:
            return points
        return False