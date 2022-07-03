from logic.routes import login, register
import pytest
from classes.response_models import *
import pydantic


User = RegisterIn(first_name="user",
                  last_name="userov",
                  email="user@example.com",
                  phone="999",
                  password="pass",
                  additional_info="")


@pytest.mark.parametrize('user_type, user_data', [
    pytest.param('sellers', User, id='Add user to db.')])
async def test_prereq_for_further_tests(user_type, user_data):
    await register.register_user(user_type=user_type, user_data=user_data)


Log1 = LoginIn(email='user@example.com',
                password='pass')

Log2 = LoginIn(email='empty_user@example.com',
                password='pass')

Log3 = LoginIn(email='user@example.com',
                password='incorrect_pass')      


@pytest.mark.parametrize('user_data, status_code', [
    pytest.param(Log1, 200, id='Positive'),
    pytest.param(Log2, 404, id='Wrong email'),
    pytest.param(Log3, 404, id='Wrong password')])
async def test_login(user_data, status_code):
    response = await login.login_user(user_data)
    assert response.status_code == status_code


async def test_login_email_validation():
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        LoginIn(email='userexample.com',
                password='')


NewPass1 = ChangePasswordIn(email='user@example.com',
                            old_password='pass',
                            new_password='pass')
                            
NewPass2 = ChangePasswordIn(email='empty_user@example.com',
                            old_password='pass',
                            new_password='pass')

NewPass3 = ChangePasswordIn(email='user@example.com',
                            old_password='incorrect_pass',
                            new_password='pass')


@pytest.mark.parametrize('user_data, status_code', [
    pytest.param(NewPass1, 200, id='Positive'),
    pytest.param(NewPass2, 404, id='Wrong email'),
    pytest.param(NewPass3, 404, id='Wrong password')])
async def test_password_changing(user_data, status_code):
    response = await login.change_password(user_data)
    assert response.status_code == status_code


async def test_change_password_email_validation():
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        ChangePasswordIn(email='userexample.com',
                         old_password='',
                         new_password='')