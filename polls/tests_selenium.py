from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class PollsSeleniumTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = Chrome()
        cls.selenium.implicitly_wait(10)
        # Crear superusuari
        user = User.objects.create_superuser('isard', 'isard@isardvdi.com', 'pirineus')
        user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login_and_create_question(self):
        # Accedeix al live server
        self.selenium.get(f'{self.live_server_url}/admin')
        # Fes login
        self.selenium.find_element(By.NAME, 'username').send_keys('isard')
        self.selenium.find_element(By.NAME, 'password').send_keys('pirineus')
        self.selenium.find_element(By.XPATH, '//input[@type="submit"]').click()

        # Assert que s'ha loguejat correctament
        self.selenium.find_element(By.XPATH, "//a[text()='Log out']")

        # Crea una nova Question
        self.selenium.get(f'{self.live_server_url}/admin/polls/question/add/')
        self.selenium.find_element(By.NAME, 'question_text').send_keys('Pregunta de prova')
        self.selenium.find_element(By.NAME, 'pub_date').send_keys('2025-01-01 00:00:00')
        self.selenium.find_element(By.XPATH, "//input[@type='submit' and @value='Save']").click()

        # Assert que la Question es veu a la llista
        self.selenium.find_element(By.LINK_TEXT, 'Pregunta de prova')

    def test_element_not_present(self):
        # Comprova que un element no existeix
        try:
            self.selenium.find_element(By.XPATH, "//a[text()='Nonexistent Element']")
            assert False, "L'element no hauria d'existir"
        except NoSuchElementException:
            pass
