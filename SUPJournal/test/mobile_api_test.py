import unittest
import requests


def register(login, password, e_mail):
    req = requests.post("http://127.0.0.1:5000/api/mobile/register",
                        json={"user": login, "pass_": password, "e_mail": e_mail})
    return req


def auth(login: str, password: str):
    req = requests.post("http://127.0.0.1:5000/api/mobile/auth",
                        json={"user": login, "pass_": password})
    return req


def delete(token, user):
    req = requests.delete("http://127.0.0.1:5000/api/mobile/delete",
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

    def test_1_register(self):
        """
        Регистрация нового пользователя
        """
        resp = register(self.user.login, self.user.password, self.user.e_mail)
        self.assertEqual(resp.status_code, 200, "Регистрация ОК")
        self.assertEqual(self.user.token, None, "Проверка отсутствия токена перед записью")
        self.user.token = resp.json()["token"]

    def test_2_another_register(self):
        """
        Регистрация существующего юзера
        """
        resp = register(self.user.login, self.user.password, self.user.e_mail)
        self.assertEqual(resp.status_code, 500)

    def test_3_auth(self):
        """
        Авторизация юзера
        """
        resp = auth(self.user.login, self.user.password)
        self.assertEqual(resp.status_code, 200, "Успешная авторизация")
        self.assertEqual(self.user.login, resp.json()["user"], "Проверка что пришел user")
        self.assertIsNotNone(resp.json()["user_id"], "Проверка что пришел user_id")

    def test_4_auth_err(self):
        """
        Проверка не успешных авторизаций
        """
        resp1 = auth("Не верный логин", self.user.login)
        self.assertEqual(resp1.status_code, 401, "Статус код, неверный юзер")
        self.assertEqual(resp1.headers["X-Error-Message"], "incorrect_user", "Заголовок, неверный юзер")
        resp2 = auth(self.user.login, "Не верный пароль")
        self.assertEqual(resp2.status_code, 401, "Статус код, неверный пароль")
        self.assertEqual(resp2.headers["X-Error-Message"], "incorrect_password", "Заголовок, не верный пароль")

    def test_5_delete_user(self):
        """
        Удаление пользователя
        """
        resp = delete(self.user.token, self.user.login)
        self.assertEqual(resp.status_code, 200, "Удаление юзера ОК")
