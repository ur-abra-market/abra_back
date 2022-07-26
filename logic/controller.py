from db.db_connector import Database
from dotenv import load_dotenv
from logic import pwd_hashing, utils
from fastapi.responses import JSONResponse
import uuid
from fastapi import HTTPException, status
from fastapi_mail import MessageSchema, FastMail
from const import const


load_dotenv()
db = Database()


async def register_user(user_type, user_data):
    if user_type not in ['sellers', 'suppliers']:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Incorrect subdomain"
        )
    is_email_unique = db.check_email_for_uniqueness(email=user_data.email)
    if not is_email_unique:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User with this email already exists"
        )
    db.add_user(user_data=user_data)
    user_id = db.get_user_id(email=user_data.email)
    hashed_password = pwd_hashing.hash_password(password=user_data.password)
    db.add_password(user_id=user_id, password=hashed_password)
    if user_type == 'sellers':
        db.add_seller(user_id=user_id)
    elif user_type == 'suppliers':
        db.add_supplier(user_id=user_id)
    return JSONResponse(
        status_code=200,
        content={"result": "Registration successfull!"}
    )


async def login_user(user_data):
    user_id = db.get_user_id(email=user_data.username)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Wrong credentials"
        )
    hashed_password_from_db = db.get_password(user_id=user_id)
    is_passwords_match = \
        pwd_hashing.check_hashed_password(password=user_data.password,
                                          hashed=hashed_password_from_db)
    if hashed_password_from_db and is_passwords_match:
        return JSONResponse(
            status_code=200,
            content={"result": "Login successfully!"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Wrong credentials"
        )


async def change_password(user_data, user_email):
    user_id = db.get_user_id(email=user_email)
    hashed_password_db = db.get_password(user_id=user_id)
    is_passwords_match = \
        pwd_hashing.check_hashed_password(password=user_data.old_password,
                                          hashed=hashed_password_db)
    if hashed_password_db and is_passwords_match:
        hashed_password_new = \
            pwd_hashing.hash_password(password=user_data.new_password)
        db.update_password(user_id=user_id,
                           password_new=hashed_password_new)
        return JSONResponse(
            status_code=200,
            content={"result": "Password changed successfully!"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Wrong old password!"
        )


async def send_email(subject, recipient, body):
    message = MessageSchema(
        subject=subject,
        recipients=recipient,
        body=body,
        subtype="html"
    )
    fm = FastMail(utils.conf)
    await fm.send_message(message=message)
    return JSONResponse(
        status_code=200,
        content={"result": "Message has been sent"}
    )


async def send_confirmation_email(email):
    encoded_token = utils.create_access_token(email)
    subject = "Email confirmation"
    recipient = [email]
    body = const.CONFIRMATION_BODY.format(token=encoded_token)
    await send_email(subject, recipient, body)
    return JSONResponse(
        status_code=200,
        content={"result": "Message has been sent"}
    )


async def receive_registration_result(token):
    try:
        decoded_token = utils.get_current_user(token)
        result = db.check_for_email(decoded_token["email"])
        if result:
            return JSONResponse(
                status_code=200,
                content={"result": "Registration successful."}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
        

async def send_reset_message(email):
    result = db.check_for_email(email)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    reset_code = str(uuid.uuid1())
    user_id = db.get_user_id(email)
    db.create_reset_code(user_id, email, reset_code)
    subject = "Сброс пароля"
    recipient = [email]
    body = const.BODY.format(email, reset_code)
    await send_email(subject, recipient, body)
    return JSONResponse(
        status_code=200,
        content={"result": "Message has been sent"}
    )


async def check_token(token):
    reset_token = db.check_reset_password_token(token)
    if not reset_token:
        raise HTTPException(
            status_code=404,
            detail="Reset token has been expired, try again."
        )
    return JSONResponse(
        status_code=200,
        content={"result": "Token is active"}
    )


async def reset_user_password(user_email,
                              user_new_password,
                              user_confirm_new_password):
    if user_new_password != user_confirm_new_password:
        raise HTTPException(
            status_code=404,
            detail="New password is not match."
        )
    user_id = db.get_user_id(user_email)
    hashed_password = pwd_hashing.hash_password(user_new_password)
    db.update_password(user_id=user_id, password_new=hashed_password)
    db.delete_token(user_email)
    return JSONResponse(
        status_code=200,
        content={"result": "Password has been changed successfuly."}
    )


async def get_products_list_for_category(category, type):
    # tmp if-clause? validate it on front?
    if type not in ['bestsellers', 'new', 'rating', 'hot', 'popular']:
        return JSONResponse(
            status_code=404,
            content={"result": f"'{type} sort-type does not exist'"}
        )

    if category == 'all':
        category_id = 'p.category_id'
    else:
        category_id = db.get_category_id_by_category_name(category)

    if not category_id:
        return JSONResponse(
            status_code=404,
            content={"result": f"'{category}' category does not exist"}
        )
        
    result = db.get_sorted_list_of_products(type=type,
                                            category_id=category_id)
    return JSONResponse(
        status_code=200,
        content={"result": result}
    )


async def get_category_path(category):
    result = db.get_category_path(category)
    if result:
        return JSONResponse(
            status_code=200,
            content={"result": result[0]}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="'{category}' category does not exist"
        )


async def get_images_for_product(product_id):
    result = db.get_images_by_product_id(product_id=product_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with product_id={product_id} is not found in db."
        )
    return JSONResponse(
        status_code=200,
        content={"result": result}
    )

    
async def get_popular_products_in_category(product_id):
    category_id = db.get_category_id_by_product_id(product_id=product_id)
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with product_id={product_id} is not found in db."
        )
    result = db.get_sorted_list_of_products(type='popular',
                                            category_id=category_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no products in this category (category_id={category_id})."
        )
    return JSONResponse(
        status_code=200,
        content={"result": result}
    )


async def get_latest_searches_for_user(user_id):
    result = db.get_latest_searches_by_user_id(user_id=user_id)
    if result:
        return JSONResponse(
            status_code=200,
            content={"result": result}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"This user (user_id={user_id}) does not have latest searches."
        )