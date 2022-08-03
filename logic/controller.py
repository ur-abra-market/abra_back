from logic import pwd_hashing, utils
from starlette.responses import JSONResponse
import uuid
from fastapi import HTTPException, status
from fastapi_mail import MessageSchema, FastMail
from logic import consts





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
            content={"result": "PASSWORD_CHANGED"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="INVALID_PASSWORD"
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
    body = consts.CONFIRMATION_BODY.format(token=encoded_token)
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
    body = consts.BODY.format(email, reset_code)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TYPE_NOT_EXIST"
        )
    if category == 'all':
        category_id = 'p.category_id'
    else:
        category_id = db.get_category_id_by_category_name(category)
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CATEGORY_NOT_FOUND"
        )
    result = db.get_sorted_list_of_products(type=type,
                                            category_id=category_id)
    return JSONResponse(
        status_code=200,
        content={"result": result}
    )
    


async def get_images_for_product(product_id):
    result = db.get_images_by_product_id(product_id=product_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )
    return JSONResponse(
        status_code=200,
        content={"result": result}
    )


async def get_similar_products_in_category(product_id):
    result = db.get_similar_products(product_id=product_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_PRODUCTS"
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
            detail="PRODUCT_NOT_FOUND"
        )
    result = db.get_sorted_list_of_products(type='popular',
                                            category_id=category_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_PRODUCTS"
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
            detail="NO_SEARCHES"
        )