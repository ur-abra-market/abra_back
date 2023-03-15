from enum import Enum
import app.database.models as models


ACCESS_TOKEN_EXPIRATION_TIME = 60 * 60 * 24  # 1 day
REFRESH_TOKEN_EXPIRATION_TIME = 60 * 60 * 24 * 14  # 14 days




class SortingTypes(Enum):
    """Used to show dropdown menu in OpenApi."""

    rating = "rating"
    price = "price"
    date = "date"
    total_orders = "total_orders"


BODY = """
    <div style="width:100%;font-family: monospace;">
        <h1>Привет, {user}</h1>
        <p>Кто-то создал запрос на сброс и смену пароля. Если это были вы, вы можете сбросить\
        и сменить свой пароль, перейдя по ссылке ниже:</p>
        <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; " href="{host}register/resetPassword/?token={reset_code}">Подтвердить</a>
        <p>Если это были не вы, пожалуйста, игнорируйте данное письмо!</p>
        <p>Ваш пароль не поменяется, если вы не перейдете по ссылке.</p>
    </div>
    """


CONFIRMATION_BODY = """
            <div style="display: flex; align-items: center; justify-content: center; flex-direction: column">
                <h3>Подтверждение электронной почты</h3>
                <br>
                <p>Благодарим вас за регистрацию на нашей платформе, ниже ссылка для подтвержения электронной почты:</p>
                <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; " href="{host}register/email-confirmation/?token={token}">Подтвердить</a>
                <p>Если вы не регистрировались на abra-market.com, пожалуйста игнорируйте данное сообщение!</p>
            </div>
    """
