ACCESS_TOKEN_EXPIRATION_TIME = 60 * 60  # 1 hour
REFRESH_TOKEN_EXPIRATION_TIME = 60 * 60 * 24 * 14  # 14 days

SQL_QUERY_FOR_BESTSELLERS = '''
    WITH product_completed_orders(product_id, total)
    AS (
        SELECT product_id, SUM(count) as total
        FROM web_platform.orders
        WHERE is_completed = 1
        GROUP BY product_id
    )
    SELECT
      p.id
    , p.name
    , p.description
    , FORMAT(pco.total, 0) AS total_orders
    , FORMAT(pp.value * (1 - IFNULL(pp.discount, 0)), 2) AS price
    , pi.image_url
    FROM web_platform.products p
        JOIN product_completed_orders pco ON pco.product_id = p.id
        JOIN web_platform.product_prices pp ON pp.product_id = p.id
        JOIN web_platform.product_images pi ON pi.product_id = p.id
                                           AND pi.serial_number = 0
    WHERE p.category_id = {}
    ORDER BY pco.total DESC
    LIMIT 6
    '''

SQL_QUERY_FOR_NEW_ARRIVALS = '''
    SELECT 
      p.id
    , p.name
    , p.description
    , DATE_FORMAT(p.datetime, '%d/%m/%Y') AS arrival_date
    , FORMAT(pp.value * (1 - IFNULL(pp.discount, 0)), 2) AS price
    , pi.image_url
    FROM web_platform.products p
        JOIN web_platform.product_prices pp ON pp.product_id = p.id
        JOIN web_platform.product_images pi ON pi.product_id = p.id
                                           AND pi.serial_number = 0
    WHERE p.category_id = {}
    ORDER BY p.datetime DESC
    LIMIT 6
    '''

SQL_QUERY_FOR_HIGHEST_RATINGS = '''
    WITH product_ratings(product_id, rating)
    AS (
        SELECT product_id, AVG(grade_overall) AS rating
        FROM web_platform.product_reviews
        GROUP BY product_id
        HAVING COUNT(1) > 1
    )
    SELECT 
      p.id
    , p.name
    , p.description
    , FORMAT(pr.rating, 2) AS rating
    , FORMAT(pp.value * (1 - IFNULL(pp.discount, 0)), 2) AS price
    , pi.image_url
    FROM web_platform.products p
        JOIN product_ratings pr ON pr.product_id = p.id
        JOIN web_platform.product_prices pp ON pp.product_id = p.id
        JOIN web_platform.product_images pi ON pi.product_id = p.id
                                           AND pi.serial_number = 0
    WHERE p.category_id = {}
    ORDER BY pr.rating DESC
    LIMIT 6
    '''

SQL_QUERY_FOR_HOT_DEALS = '''
    WITH product_completed_orders(product_id, total)
    AS (
        SELECT product_id, SUM(count) as total
        FROM web_platform.orders
        WHERE is_completed = 1
        GROUP BY product_id
    )
    SELECT 
      p.id
    , p.name
    , p.description
    , FORMAT(pco.total, 0) AS total_orders
    , FORMAT(pp.value * (1 - IFNULL(pp.discount, 0)), 2) AS price
    , pi.image_url
    FROM web_platform.products p
        JOIN product_completed_orders pco ON pco.product_id = p.id
        JOIN web_platform.product_prices pp ON pp.product_id = p.id
        JOIN web_platform.product_images pi ON pi.product_id = p.id
                                           AND pi.serial_number = 0
    WHERE p.category_id = {}
        AND p.with_discount = 1
    ORDER BY pco.total DESC
    LIMIT 6
    '''

SQL_QUERY_FOR_POPULAR_NOW = '''
    WITH product_completed_orders(product_id, total)
    AS (
        SELECT product_id, SUM(count) as total
        FROM web_platform.orders
        WHERE is_completed = 1
            AND DATEDIFF(NOW(), datetime) < 31 
        GROUP BY product_id
    )
    SELECT 
      p.id
    , p.name
    , p.description
    , FORMAT(pco.total, 0) AS total_orders
    , FORMAT(pp.value * (1 - IFNULL(pp.discount, 0)), 2) AS price
    , pi.image_url
    FROM web_platform.products p
        JOIN product_completed_orders pco ON pco.product_id = p.id
        JOIN web_platform.product_prices pp ON pp.product_id = p.id
        JOIN web_platform.product_images pi ON pi.product_id = p.id
                                           AND pi.serial_number = 0
    WHERE p.category_id = {}
    ORDER BY pco.total DESC
    LIMIT 6
    '''

SQL_QUERY_FOR_CATEGORY_PATH = '''
    WITH RECURSIVE category_path (parent_id, cat_path) AS
    (
        SELECT parent_id, CONCAT("/", name)
        FROM web_platform.categories c 
        WHERE name = "{}"
        
        UNION ALL 
        
        SELECT c.parent_id, CONCAT("/", c.name, cp.cat_path)
        FROM category_path cp
            JOIN web_platform.categories c ON c.id = cp.parent_id
        WHERE cp.parent_id IS NOT NULL
    )
    SELECT cat_path
    FROM category_path
    WHERE parent_id IS NULL
    '''


BODY = """
    <!DOCTYPE html>
    <html>
    <title>Сброс пароля</title>
    <body>
    <div style="width:100%;font-family: monospace;">
        <h1>Привет, {}</h1>
        <p>Кто-то создал запрос на сброс и смену пароля. Если это были вы, вы можете сбросить\
        и сменить свой пароль, нажав на эту кнопку.</p>
        <form action="http://localhost:8000/login/forgot-password?reset_password_token={}">
            <input type="submit" value="Подтвердить" />
        </form>
        <p>Если это были не вы, пожалуйста, игнорируйте данное письмо!</p>
        <p>Ваш пароль не поменяется, если вы не нажмете кнопку подтверждения.</p>
    </div>
    </body>
    </html>
    """


SQL_QUERY_FOR_CHECK_TOKEN = '''
    SELECT * 
    FROM reset_tokens
    WHERE status = "1" 
        AND reset_code = {}
    '''

CONFIRMATION_BODY = """
<!DOCTYPE html>
    <html>
    <head>

    </head>
    <body>
        <div style = "display: flex; align-items: center; justify-content:
        center; flex-direction: column">
            <h3>Подтверждение электронной почты</h3>
            <br>
            <p>Благодарим вас за регистрацию на нашей платформе, ниже ссылка для подтвержения электронной почты</p>
            <a style="margin-top: lrem; padding: lrem; border-radius: 0.5rem; font-size: lrem; text-decoration: none; background; #0275d8; color: white;" href="http://localhost:8000/register/email-confirmation/?token={token}">
            Подтвердите вашу почту
            </a>
            <p>Если вы не регистрировались на !!!ссылка!!!, пожалуйста игнорируйте данное сообщение!</p>
        </div>
    </body>
    </html>
"""