class OldPasswordMismatchException(Exception):
    def __init__(self, message='Старый пароль неверный'):
        super().__init__(message)


class SamePasswordException(Exception):
    def __init__(self, message='Новый пароль совпадает со старым'):
        super().__init__(message)


class PasswordsDoNotMatchException(Exception):
    def __init__(self, message='Новые пароли не совпадают'):
        super().__init__(message)
