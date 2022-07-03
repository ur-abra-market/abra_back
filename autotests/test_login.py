from logic.routes import login, register
import pytest
from classes.response_models import *
import pydantic

# in process
'''
User = RegisterIn(first_name="user",
                  last_name="userov",
                  email="user@example.com",
                  phone="123",
                  password="pass",
                  additional_info="")

async def register_test_user(user_data):
    await register.register_user(user_type='sellers', user_data=user_data)
    return

register_test_user(user_data=User)
'''


Cred1 = LoginIn(email='user@example.com',
                password='pass')

Cred2 = LoginIn(email='useruser@example.com',
                password='pass')

Cred3 = LoginIn(email='user@example.com',
                password='pwd')      


@pytest.mark.parametrize('user_data, status_code', [
    pytest.param(Cred1, 200, id='Positive'),
    pytest.param(Cred2, 404, id='Wrong email'),
    pytest.param(Cred3, 404, id='Wrong password')])
async def test_login(user_data, status_code):
    response = await login.login_user(user_data)
    assert response.status_code == status_code


async def test_login_email_validation():
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        LoginIn(email='userexample.com',
                password='')
