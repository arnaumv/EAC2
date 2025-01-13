from django.test import TestCase

from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class PollsSeleniumTests(StaticLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)
        
        # Crear superusuario para pruebas
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login_and_create_question(self):
        # Acceder al panel de administración
        self.selenium.get(f'{self.live_server_url}/admin')

        # Iniciar sesión
        self.selenium.find_element(By.NAME, 'username').send_keys('isard')
        self.selenium.find_element(By.NAME, 'password').send_keys('pirineus')
        self.selenium.find_element(By.XPATH, '//input[@type="submit"]').click()

        # Esperar a que el botón "Log out" sea visible y clickeable
        try:
            WebDriverWait(self.selenium, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Log out']"))
            )
        except TimeoutException:
            with open("debug_login_page.html", "w") as f:
                f.write(self.selenium.page_source)
            self.fail("No se encontró el botón 'Log out' después de iniciar sesión")

        # Crear una nueva pregunta (Question)
        self.selenium.get(f'{self.live_server_url}/admin/polls/question/add/')

        # Esperar a que los campos de fecha y hora estén disponibles
        try:
            pub_date_field_0 = WebDriverWait(self.selenium, 10).until(
                EC.visibility_of_element_located((By.NAME, 'pub_date_0'))
            )
            pub_date_field_1 = WebDriverWait(self.selenium, 10).until(
                EC.visibility_of_element_located((By.NAME, 'pub_date_1'))
            )
        except TimeoutException:
            self.fail("No se encontró el campo 'pub_date' en la página de agregar pregunta")

        # Rellenar el formulario
        self.selenium.find_element(By.NAME, 'question_text').send_keys('Pregunta de prueba')
        pub_date_field_0.send_keys('2025-01-01')  # Fecha
        pub_date_field_1.send_keys('00:00:00')   # Hora
        self.selenium.find_element(By.XPATH, "//input[@type='submit' and @value='Save']").click()

        # Esperar que la página se recargue y mostrar la pregunta creada
        try:
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Question object'))
            )
        except TimeoutException:
            # Guardamos la página para poder depurar
            with open("debug_after_create_question.html", "w") as f:
                f.write(self.selenium.page_source)
            self.fail("La pregunta no aparece en la lista después de ser creada")

        # Verificar que el enlace con "Question object" aparece en la lista
        try:
            self.selenium.find_element(By.PARTIAL_LINK_TEXT, 'Question object')
        except NoSuchElementException:
            self.fail("La pregunta no aparece en la lista después de ser creada")
        
        # Verificar que no exista un elemento que no deba estar presente
        try:
            self.selenium.find_element(By.XPATH, "//button[text()='Non-existent Button']")
            assert False, "Se ha encontrado un elemento que no debería existir"
        except NoSuchElementException:
            pass  # Lo esperado, el elemento no debe existir
