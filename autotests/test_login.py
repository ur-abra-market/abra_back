from logic.routes import login, register
import pytest
from classes.response_models import *
import pydantic


class Dict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__getitem__


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


Log1 = LoginIn(username='user@example.com',
                password='pass')

Log2 = LoginIn(username='empty_user@example.com',
                password='pass')

Log3 = LoginIn(username='user@example.com',
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


NewPass1 = ChangePasswordIn(old_password='pass',
                            new_password='pass')
                            
NewPass2 = ChangePasswordIn(old_password='pass',
                            new_password='pass')

NewPass3 = ChangePasswordIn(old_password='incorrect_pass',
                            new_password='pass')

pwd_user = Dict(email='user@example.com')
pwd_user_wrong = Dict(email='userexample.com')

@pytest.mark.parametrize('user_data, user_email, status_code', [
    pytest.param(NewPass1, pwd_user, 200, id='Positive'),
    pytest.param(NewPass2, pwd_user_wrong, 404, id='Wrong email'),
    pytest.param(NewPass3, pwd_user, 404, id='Wrong password')])
async def test_password_changing(user_data, user_email, status_code):
    response = await login.change_password(user_data, user_email)
    assert response.status_code == status_code
