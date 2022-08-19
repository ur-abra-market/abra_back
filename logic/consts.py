ACCESS_TOKEN_EXPIRATION_TIME = 60 * 60 * 24  # 1 day
REFRESH_TOKEN_EXPIRATION_TIME = 60 * 60 * 24 * 14  # 14 days

QUERY_FOR_BESTSELLERS = '''
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

QUERY_FOR_NEW_ARRIVALS = '''
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

QUERY_FOR_HIGHEST_RATINGS = '''
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

QUERY_FOR_HOT_DEALS = '''
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
        AND p.with_discount IS True
    ORDER BY pco.total DESC
    LIMIT 6
    '''

QUERY_FOR_POPULAR_NOW = '''
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

# in progress
QUERY_FOR_SIMILAR_PRODUCTS = '''
    SELECT
      id
    , name
    , description
    , with_discount
    , count
    FROM web_platform.products p
    WHERE p.id != {}
    '''

QUERY_FOR_CATEGORY_PATH = '''
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


QUERY_FOR_VARIATONS = '''
    SELECT
    cvt.name AS param
    , cvv.value AS value
    FROM web_platform.product_variation_values pvv 
        JOIN web_platform.category_variation_values cvv ON cvv.id = pvv.variation_value_id
        JOIN web_platform.category_variation_types cvt ON cvt.id = cvv.variation_type_id 
    WHERE pvv.product_id = {}
    '''


QUERY_FOR_PROPERTIES = '''
    SELECT
    cpt.name AS param
    , cpv.value AS value
    FROM web_platform.product_property_values ppv 
        JOIN web_platform.category_property_values cpv ON cpv.id = ppv.property_value_id
        JOIN web_platform.category_property_types cpt ON cpt.id = cpv.property_type_id
    WHERE ppv.product_id = {}
    '''


QUERY_FOR_COLORS = '''
    SELECT cpv.value AS color
    FROM web_platform.product_property_values ppv 
        JOIN web_platform.category_property_values cpv ON cpv.id = ppv.property_value_id
        JOIN web_platform.category_property_types cpt ON cpt.id = cpv.property_type_id
    WHERE ppv.product_id = {}
        AND cpt.name = 'Color'
    '''


BODY = """
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
    """


QUERY_FOR_CHECK_TOKEN = '''
    SELECT * 
    FROM reset_tokens
    WHERE status IS True
        AND reset_code = {}
    '''


CONFIRMATION_BODY = """
            <div style="display: flex; align-items: center; justify-content: center; flex-direction: column">
                <h3>Подтверждение электронной почты</h3>
                <br>
                <p>Благодарим вас за регистрацию на нашей платформе, ниже ссылка для подтвержения электронной почты</p>
                <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; " href="http://localhost:8000/register/email-confirmation/?token={token}">
                Подтвердите вашу почту
                </a>
                <p>Если вы не регистрировались на !!!ссылка!!!, пожалуйста игнорируйте данное сообщение!</p>
            </div>
    """

QUERY_FOR_PAGINATION_PRODUCT_ID = """
    SELECT id
    FROM web_platform.products
    WHERE category_id = {}
    LIMIT {}
    OFFSET {}
    """

QUERY_FOR_PAGINATION_MAIN = """
    SELECT
      p.name
    , CONVERT(p.grade_average, CHAR) AS grade_average
    , CONVERT(IFNULL(pp.value, 0), CHAR) AS value_price
    , IFNULL(pp.quantity, 0) AS quantity 
    , COUNT(pr.id) AS total_reviews
    , IFNULL(FLOOR(o.count), 0) AS total_orders
    FROM web_platform.products p
        LEFT OUTER JOIN web_platform.orders o ON o.product_id = p.id
                                AND o.is_completed = 1
        LEFT OUTER JOIN web_platform.product_prices pp ON pp.product_id = p.id
                            AND pp.is_active = 1
                            AND pp.quantity = 100
        LEFT OUTER JOIN web_platform.product_reviews pr ON pr.product_id = p.id
    WHERE p.id = {}
    GROUP BY p.id, p.name, p.grade_average, pp.value 
    """

QUERY_FOR_ACTUAL_DEMAND = """
    SELECT CONVERT(SUM(count), CHAR) AS number_of_orders
    FROM web_platform.orders
    WHERE product_id = {}
        AND is_completed IS True
        AND DATEDIFF(NOW(), datetime) < 31
    """

QUERY_FOR_PRICES = """
    SELECT
      CONVERT(value, CHAR) AS value 
    , quantity 
    , CONVERT(discount, CHAR) AS discount  
    , CONVERT(start_date, CHAR) AS start_date
    , CONVERT(end_date, CHAR) AS end_date
    FROM web_platform.product_prices
    WHERE product_id = {}
        AND is_active IS TRUE 
    """

QUERY_FOR_SUPPLIER_INFO = """
    SELECT
      s.customer_name
    , CONVERT(s.grade_average, CHAR) AS grade_average
    , s.count
    , CASE 
        WHEN DATEDIFF(NOW(), u.datetime) < 365 THEN FLOOR(CEIL(DATEDIFF(NOW(), u.datetime) / 31))
        ELSE FLOOR(ROUND(DATEDIFF(NOW(), u.datetime) / 365))
      END value
    , CASE 
        WHEN DATEDIFF(NOW(), u.datetime) < 365 THEN 'months'
        ELSE 'years'
      END period
    FROM web_platform.users u 
        JOIN web_platform.suppliers s ON s.user_id = u.id
        JOIN web_platform.products p ON p.supplier_id = s.id 
                                    AND p.id = {}
    """

QUERY_FOR_REVIEWS = """
    SELECT pr.seller_id, pr.text, CONVERT(pr.grade_overall, CHAR) AS grade_overall, CONVERT(pr.datetime, CHAR) AS datetime, prp.image_url 
    FROM web_platform.product_review_photos prp RIGHT JOIN web_platform.product_reviews pr
    ON prp.product_review_id = pr.id
    WHERE pr.product_id = {product_id}
    ORDER BY pr.datetime DESC
    LIMIT 10
"""

QUERY_FOR_PRODUCT_GRADE = """
    SELECT 
      CONVERT(p.grade_average, CHAR) AS grade_average
    , COUNT(pr.id) AS count
    FROM web_platform.products p
        LEFT JOIN web_platform.product_reviews pr ON pr.product_id = p.id
    WHERE p.id = {}
    GROUP BY p.grade_average 
    """

QUERY_FOR_PRODUCT_GRADE_DETAILS = """
    SELECT 
      grade_overall 
    , COUNT(1) AS count
    FROM web_platform.product_reviews pr 
    WHERE product_id = {}
    GROUP BY grade_overall
    ORDER BY grade_overall DESC
    """