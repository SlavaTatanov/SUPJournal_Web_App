# SUPJournal_Web_App

Веб-приложение - журнал тренировок (ориентирован на занятия на САП-борде). Сервер связан с сайтом и с мобильным приложением.
Сервер принимает тренировки с мобильного приложения, и сохраняет их в базу данных.
Сайт используется для отображения тренировок конкретного пользователя.

![Снимок экрана от 2023-06-06 19-52-42](https://github.com/SlavaTatanov/SUPJournal_Web_App/assets/107018438/17fa9b94-d2a0-427b-b046-a290a8e93469)

Мобильное приложение помимо отображения тренировок служит для их записи в формате GPX.
Аутентификация реализована по типу передачи сервером JWT токена на мобильное устройство если пользователь корректно вводит логин/пароль.

Мобильное приложение находится здесь -> https://github.com/SlavaTatanov/SUPJournal-Android-APP

![SUPJournal](https://user-images.githubusercontent.com/107018438/220532782-7141da88-1c98-4db1-bf63-f175806c970e.png)

На данный момент реализована только возможность регистрации и аутентификации пользователей через сервер. 
Так же реализован модуль отображения GPX трека на карте и его частичного анализа (погода во время тренировки, расстояние, время).
