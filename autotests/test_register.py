from logic.routes import register
import pytest
from classes.response_models import *
import pydantic
from logic import utils


rand_num = utils.get_rand_number()


Reg1 = RegisterIn(first_name='user',
                   last_name='userov',
                   email=f'user_seller{rand_num}@example.com',
                   phone='999',
                   password='pass')

Reg2 = RegisterIn(first_name='user',
                   last_name='userov',
                   email=f'user_seller{rand_num}@example.com',
                   phone='999',
                   password='pass')

Reg3 = RegisterIn(first_name='user',
                   last_name='userov',
                   email=f'user_supplier{rand_num}@example.com',
                   phone='999',
                   password='pass')


@pytest.mark.parametrize('user_type, user_data, status_code', [
    pytest.param('sellers', Reg1, 200, id='Positive seller'),
    pytest.param('sellers', Reg2, 404, id='Not unique email'),
    pytest.param('suppliers', Reg3, 200, id='Positive supplier')])
async def test_register(user_type, user_data, status_code):
    response = await register.register_user(user_type, user_data)
    assert response.status_code == status_code


async def test_register_email_validation():
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        RegisterIn(first_name='user',
                   last_name='userov',
                   email='userexample.com',
                   phone='999',
                   password='pass')
