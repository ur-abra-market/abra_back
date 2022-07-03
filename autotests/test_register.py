from logic.routes import register
import pytest
from classes.response_models import *
import pydantic
from logic import utils


rand_num = utils.get_rand_number()


Cred1 = RegisterIn(first_name='Elon',
                   last_name='Musk',
                   email=f'elon_seller{rand_num}@gmail.com',
                   phone='12',
                   password='pass')

Cred2 = RegisterIn(first_name='Elon',
                   last_name='Musk',
                   email=f'elon_seller{rand_num}@gmail.com',
                   phone='12',
                   password='pass')

Cred3 = RegisterIn(first_name='Elon',
                   last_name='Musk',
                   email=f'elon_supplier{rand_num}@gmail.com',
                   phone='12',
                   password='pass')


@pytest.mark.parametrize('user_type, user_data, status_code', [
    pytest.param('sellers', Cred1, 200, id='Positive seller'),
    pytest.param('sellers', Cred2, 404, id='Not unique email'),
    pytest.param('suppliers', Cred3, 200, id='Positive supplier')])
async def test_register(user_type, user_data, status_code):
    response = await register.register_user(user_type, user_data)
    assert response.status_code == status_code


async def test_register_email_validation():
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        RegisterIn(first_name='Elon',
                   last_name='Musk',
                   email='elongmail.com',
                   phone='12',
                   password='pass')
