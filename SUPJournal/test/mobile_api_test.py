import unittest
import requests

URL = "http://127.0.0.1:5000"

def register(login, password, e_mail):
    req = requests.post(f"{URL}/api/mobile/register",
                        json={"user": login, "pass_": password, "e_mail": e_mail})
    return req

def auth(login: str, password: str):
    req = requests.post(f"{URL}/api/mobile/auth",
                        json={"user": login, "pass_": password})
    return req

def check(token, user):
    req = requests.get(f"{URL}/api/mobile/check",
                       headers={"Authorization": f"Bearer {token}"},
                       params={"user": user})
    return req

def change_password(user: str,password: str, new_password: str, token: str):
    req = requests.post(f"{URL}/api/mobile/change_password",
                        headers={"Authorization": f"Bearer {token}"},
                        json={"user": user, "password": password, "new_password": new_password})
    return req


def create_training(token, login, file):
    with open(file, "rb") as gpx_file:
        req = requests.post(f"{URL}/api/mobile/create_training",
                            headers={"Authorization": f"Bearer {token}", "X-User": login},
                            files={"gpx": gpx_file})
        return req


def get_training(token):
    req = requests.get(f"{URL}/api/mobile/get_training",
                       params={"training_id": "123"},
                       headers={"Authorization": f"Bearer {token}"})
    return req

def delete(token, user):
    req = requests.delete(f"{URL}/api/mobile/delete",
                          headers={"Authorization": f"Bearer {token}"},
                          json={"user": user})
    return req


class User:
    def __init__(self, login, password, e_mail, token=None):
        self.login = login
        self.password = password
        self.e_mail = e_mail
        self.token = token
        self.old_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3Njg4MzA2MCwi" \
                         "anRpIjoiMDIyYTA5YTgtYWRjZi00Y2EwLTljY2UtMzM3YzFiOGNhYjc1IiwidHlwZSI6ImFjY2VzcyIsInN1" \
                         "YiI6IlNsYXZhVGF0YW5vdiIsIm5iZiI6MTY3Njg4MzA2MCwiZXhwIjoxNjc2ODgzOTYwfQ.eY6vuxVBv8Pm5Q-" \
                         "w8WmfXEnDkoTnQSC0hIpa3vSvXbM"


class MobileApiTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.user = User("IvanIvanovich", "test_password", "test@mail.world")

    def test_001_register(self):
        """
        Регистрация нового пользователя
        """
        resp = register(self.user.login, self.user.password, self.user.e_mail)
        self.assertEqual(resp.status_code, 200, "Регистрация ОК")
        self.assertEqual(self.user.token, None, "Проверка отсутствия токена перед записью")
        self.user.token = resp.json()["token"]

    def test_002_err_register(self):
        """
        Ошибочные регистрации
        """
        resp = register(self.user.login, self.user.password, self.user.e_mail)
        self.assertEqual(resp.status_code, 409)
        resp1 = register(self.user.login, self.user.password, "invalid@gmail.co")
        self.assertEqual(resp1.status_code, 400, "Неверный email")
        self.assertEqual(resp1.headers["X-Error-Message"], "invalid_email", "Сообщение неверный email")


    def test_003_auth(self):
        """
        Авторизация юзера
        """
        resp = auth(self.user.login, self.user.password)
        self.assertEqual(resp.status_code, 200, "Успешная авторизация")
        self.assertEqual(self.user.login, resp.json()["user"], "Проверка что пришел user")
        self.assertIsNotNone(resp.json()["user_id"], "Проверка что пришел user_id")

    def test_004_auth_err(self):
        """
        Проверка не успешных авторизаций
        """
        resp1 = auth("Не верный логин", self.user.login)
        self.assertEqual(resp1.status_code, 401, "Статус код, неверный юзер")
        self.assertEqual(resp1.headers["X-Error-Message"], "incorrect_user", "Заголовок, неверный юзер")
        resp2 = auth(self.user.login, "Не верный пароль")
        self.assertEqual(resp2.status_code, 401, "Статус код, неверный пароль")
        self.assertEqual(resp2.headers["X-Error-Message"], "incorrect_password", "Заголовок, не верный пароль")

    def test_005_check(self):
        """
        Проверка токена
        """
        resp = check(self.user.token, self.user.login)
        self.assertEqual(resp.status_code, 200, "Статус код, проверка токена")

    def test_006_err_check(self):
        """
        Неуспешные проверки токена
        """
        resp1 = check(self.user.old_token, self.user.login)
        self.assertEqual(resp1.status_code, 401, "Статус код, просроченный токен")
        self.assertEqual(resp1.headers["Content-Type"], "application/json", "Проверка содержимого")
        self.assertEqual(resp1.json()["msg"], "Token has expired", "Сообщение о просроченном токене")
        resp2 = check(self.user.token, None)
        self.assertNotEqual(resp2.headers["Content-Type"], "application/json", "body нет")
        self.assertEqual(resp2.status_code, 403, "Статус код неверный токен для этого пользователя")
        self.assertEqual(resp2.headers["X-Error-Message"], "access_denied", "Сообщение в заголовке что доступа нет")

    def test_007_change_pass(self):
        """
        Проверка смены пароля
        """
        new_pass = "new pass"
        resp1 = change_password(self.user.login, self.user.password, new_pass, self.user.token)
        self.assertEqual(resp1.status_code, 200, "Смена пароля статус код")
        self.user.password = new_pass
        resp2 = auth(self.user.login, self.user.password)
        self.assertEqual(resp2.status_code, 200, "Авторизация с новым паролем")

    def test_008_err_change_pass(self):
        """
        Неуспешная смена пароля
        """
        resp1 = change_password(self.user.login, "Неверный пароль", "Новый пароль", self.user.token)
        self.assertEqual(resp1.status_code, 401, "Передача неверного действующего пароля")
        self.assertTrue("X-Error-Message" in resp1.headers, "Проверка ключа в заголовке")
        self.assertEqual(resp1.headers["X-Error-Message"], "incorrect_password", "Неверный пароль, сообщение в заголовке")
        resp2 = change_password(self.user.login, self.user.password, "Новый пароль", self.user.old_token)
        self.assertEqual(resp2.status_code, 401, "Не валид токен")
        self.assertFalse("X-Error-Message" in resp2.headers, "Проверка ключа в заголовке")
        self.assertEqual(resp2.headers["Content-Type"], "application/json", "Проверка содержимого")
        self.assertEqual(resp2.json()["msg"], "Token has expired", "Сообщение о просроченном токене")


    def test_009_create_training(self):
        """
        Создание тренировки
        """
        resp = create_training(self.user.token, self.user.login, "test.gpx")
        self.assertEqual(resp.status_code, 200, "Статус код, создание тренировки")
        create_training(self.user.token, self.user.login, "test1.gpx")
        create_training(self.user.token, self.user.login, "test2.gpx")


    # def test_010_delete_user(self):
    #     """
    #     Удаление пользователя
    #     """
    #     resp = delete(self.user.token, self.user.login)
    #     self.assertEqual(resp.status_code, 200, "Удаление юзера ОК")
