from flask import url_for
from flask_testing import LiveServerTestCase
from selenium import webdriver
import multiprocessing

import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.common.by import By

multiprocessing.set_start_method("fork", force=True)

from .. import app
from .. import models

class TestUserTakesTheTest(LiveServerTestCase):
    def create_app(self):
        # Fichier de config uniquement pour les tests.
        app.config.from_object('fbapp.tests.config')
        return app

    # Méthode exécutée avant chaque test
    def setUp(self):
        """Setup the test driver and create test users"""
        # Le navigateur est Firefox
        self.driver = webdriver.Firefox()
        self.driver.set_window_size(1268, 900)
        # Ajout de données dans la base.
        models.init_db()
        self.wait = ui.WebDriverWait(self.driver, 10)
        self.result_page = url_for('result',
                            first_name=app.config['FB_USER_NAME'],
                            id=app.config['FB_USER_ID'],
                            gender=app.config['FB_USER_GENDER'],
                            _external=True)

    # Méthode exécutée après chaque test
    def tearDown(self):
        self.driver.quit()

    def test_user_login(self):
        self.driver.get(self.get_server_url())
        self.clicks_on_login()
        self.sees_login_page()
        self.submits_form()
        # On revient à notre site.
        self.driver.switch_to.window(self.driver.window_handles[0])
        # On attend que la fenêtre de Facebook se ferme,
        # donc de n'avoir plus qu'une fenêtre d'ouverte.
        self.wait.until(lambda driver: len(self.driver.window_handles) == 1)
        assert self.driver.current_url == 'http://localhost:8943/'
        
    def clicks_on_login(self):
        # Element contenant l'iframe
        button = self.get_el(".fb-login-button")
        # On attend que l'iframe soit chargée
        self.wait.until(lambda driver: self.driver.find_element(By.TAG_NAME, "iframe").is_displayed())
        # Clic sur l'élément
        ActionChains(self.driver).click(button).perform()
        
    def get_el(self, selector):
        return self.driver.find_element(By.CSS_SELECTOR, selector)
    
    def sees_login_page(self):
        # On attend d'avoir plus d'une fenêtre ouverte.
        self.wait.until(lambda driver: len(self.driver.window_handles) > 1)
        # switch_to permet de changer de fenêtre.
        # window_handles renvoie une liste contenant toutes les fenêtres ouvertes
        # par ordre d'ouverture.
        # La fenêtre d'authentification étant la dernière ouverte,
        # c'est la dernière de la liste.
        self.driver.switch_to.window(self.driver.window_handles[-1])
        # On attend que la page ait fini de charger.
        self.wait.until(lambda driver: self.get_el('#email'))
        assert self.driver.current_url.startswith('https://www.facebook.com/login.php') # <3 Python

    def enter_text_field(self, selector, text):
        # On trouve le champ à remplir.
        text_field = self.get_el(selector)
        # On enlève les valeurs qui y sont peut-être déjà.
        text_field.clear()
        # On ajoute le texte voulu dans le champ de formulaire.
        text_field.send_keys(text)

    def submits_form(self):
        # Le champ email a l'id email
        self.enter_text_field('#email', app.config['FB_USER_EMAIL'])
        # Le champ password a l'id pass
        self.enter_text_field('#pass', app.config['FB_USER_PW'])
        # On clique sur le bouton de soumission
        self.get_el('#loginbutton input[name=login]').click()