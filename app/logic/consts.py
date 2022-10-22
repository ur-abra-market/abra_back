ACCESS_TOKEN_EXPIRATION_TIME = 60 * 60 * 24  # 1 day
REFRESH_TOKEN_EXPIRATION_TIME = 60 * 60 * 24 * 14  # 14 days


QUERY_FOR_COMPILATION = '''
    SELECT 
      p.id
    , p.name
    , p.description
    , p.total_orders
    , CONVERT(p.grade_average, CHAR) AS grade_average
    , DATE_FORMAT(p.datetime, '%d/%m/%Y') AS date_added
    , p.with_discount
    , FORMAT(pp.value * (1 - IFNULL(pp.discount, 0)), 2) AS price_include_discount
    , pp.min_quantity 
    , pi.image_url
    FROM products p
        JOIN product_prices pp ON pp.product_id = p.id
                                           AND CONVERT_TZ(CONVERT_TZ(NOW(),'+00:00','+03:00'),'+00:00','+03:00') BETWEEN pp.start_date AND IFNULL(pp.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
                                           AND pp.min_quantity = (SELECT MIN(min_quantity)
    								   		    			  FROM product_prices pp2
                                                              WHERE pp2.product_id = p.id
                                                                AND CONVERT_TZ(CONVERT_TZ(NOW(),'+00:00','+03:00'),'+00:00','+03:00') BETWEEN pp2.start_date AND IFNULL(pp2.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y')))
        JOIN product_images pi ON pi.product_id = p.id
                                           AND pi.serial_number = 0
    WHERE p.category_id = {category_id}
        AND p.is_active = 1
    {where_clause}
    ORDER BY {order_by} DESC
    LIMIT {page_size}
    OFFSET {products_to_skip}
    '''

# unactive - have questions
QUERY_FOR_POPULAR_NOW = '''
    SELECT 
      p.id
    , p.name
    , p.description
    , p.total_orders
    , p.grade_average
    , FORMAT(pp.value * (1 - IFNULL(pp.discount, 0)), 2) AS price
    , pp.min_quantity 
    , pi.image_url
    FROM products p
        JOIN product_prices pp ON pp.product_id = p.id
                                           AND CONVERT_TZ(CONVERT_TZ(NOW(),'+00:00','+03:00'),'+00:00','+03:00') BETWEEN pp.start_date AND IFNULL(pp.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
                                           AND pp.min_quantity = (SELECT MIN(min_quantity)
                                                              FROM product_prices pp2
                                                              WHERE pp2.product_id = p.id
                                                                AND CONVERT_TZ(CONVERT_TZ(NOW(),'+00:00','+03:00'),'+00:00','+03:00') BETWEEN pp2.start_date AND IFNULL(pp2.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y')))
        JOIN product_images pi ON pi.product_id = p.id
                                           AND pi.serial_number = 0
    WHERE p.category_id = {category_id}
        AND p.is_active = 1
    ORDER BY p.total_orders DESC
    LIMIT {page_size}
    OFFSET {products_to_skip}
    '''

# in progress
QUERY_FOR_SIMILAR_PRODUCTS = '''
    SELECT
      id
    , name
    , description
    , with_discount
    FROM products p
    WHERE p.id != {product_id}
        AND p.category_id = {category_id}
        AND p.is_active = 1
    '''

QUERY_FOR_CATEGORY_PATH = '''
    WITH RECURSIVE category_path (parent_id, cat_path) AS
    (
        SELECT parent_id, CONCAT("/", name)
        FROM categories c 
        WHERE name = "{}"
        
        UNION ALL 
        
        SELECT c.parent_id, CONCAT("/", c.name, cp.cat_path)
        FROM category_path cp
            JOIN categories c ON c.id = cp.parent_id
        WHERE cp.parent_id IS NOT NULL
    )
    SELECT cat_path
    FROM category_path
    WHERE parent_id IS NULL
    '''


QUERY_FOR_VARIATIONS = '''
    SELECT
    cvt.name AS param
    , cvv.value AS value
    FROM product_variation_values pvv 
        JOIN category_variation_values cvv ON cvv.id = pvv.variation_value_id
        JOIN category_variation_types cvt ON cvt.id = cvv.variation_type_id 
    WHERE pvv.product_id = {}
    '''


QUERY_FOR_PROPERTIES = '''
    SELECT
    cpt.name AS param
    , cpv.value AS value
    FROM product_property_values ppv 
        JOIN category_property_values cpv ON cpv.id = ppv.property_value_id
        JOIN category_property_types cpt ON cpt.id = cpv.property_type_id
    WHERE ppv.product_id = {}
    '''


QUERY_FOR_COLORS = '''
    SELECT cpv.value AS color
    FROM product_property_values ppv 
        JOIN category_property_values cpv ON cpv.id = ppv.property_value_id
        JOIN category_property_types cpt ON cpt.id = cpv.property_type_id
    WHERE ppv.product_id = {}
        AND cpt.name = 'Color'
    '''


BODY = """
    <div style="width:100%;font-family: monospace;">
        <h1>Привет, {user}</h1>
        <p>Кто-то создал запрос на сброс и смену пароля. Если это были вы, вы можете сбросить\
        и сменить свой пароль, перейдя по ссылке ниже:</p>
        <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; " href="{host}register/email-confirmation/?token={reset_code}">Подтвердить</a>
        <p>Если это были не вы, пожалуйста, игнорируйте данное письмо!</p>
        <p>Ваш пароль не поменяется, если вы не перейдете по ссылке.</p>
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
                <p>Благодарим вас за регистрацию на нашей платформе, ниже ссылка для подтвержения электронной почты:</p>
                <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; " href="{host}register/email-confirmation/?token={token}">Подтвердить</a>
                <p>Если вы не регистрировались на abra-market.com, пожалуйста игнорируйте данное сообщение!</p>
            </div>
    """

QUERY_FOR_PAGINATION_CTE = """
     properties_{type} AS (
	SELECT ppv.product_id
	FROM category_property_values cpv 
		JOIN product_property_values ppv ON ppv.property_value_id = cpv.id
                                                     AND cpv.property_type_id = {property_type_id}
                                                     AND cpv.value = '{type_value}'
    )
    """

QUERY_FOR_PAGINATION_PRODUCT_ID = """
    {cte}
    SELECT p.id, COUNT(1) OVER() AS total_products
    FROM products p 
        JOIN product_prices pp ON pp.product_id = p.id
                                            AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp.start_date AND IFNULL(pp.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
                                            AND pp.min_quantity = (SELECT MIN(min_quantity)
                                                            FROM product_prices pp2
                                                            WHERE pp2.product_id = p.id
                                                                AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp2.start_date AND IFNULL(pp2.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y')))
        {cte_tables}
    {where_filters}
    ORDER BY {sort_type} {order}
    LIMIT {page_size}
    OFFSET {products_to_skip}
"""

QUERY_FOR_PAGINATION_INFO = """
    SELECT
      p.name
    , CONVERT(p.grade_average, CHAR) AS grade_average
    , CONVERT(IFNULL(pp.value, 0), CHAR) AS value_price
    , IFNULL(pp.min_quantity, 0) AS min_quantity 
    , p.with_discount
    , CONVERT(p.datetime, CHAR) AS datetime
    , COUNT(pr.id) AS total_reviews
    , p.total_orders
    FROM products p
        JOIN product_prices pp ON pp.product_id = p.id
                            AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp.start_date AND IFNULL(pp.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
                            AND pp.min_quantity = (SELECT MIN(min_quantity)
                                               FROM product_prices pp2
                                               WHERE pp2.product_id = p.id
                                                    AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp2.start_date AND IFNULL(pp2.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y')))
        LEFT OUTER JOIN product_reviews pr ON pr.product_id = p.id
    WHERE p.id = {}
    GROUP BY p.id, p.name, p.grade_average, pp.value, pp.min_quantity
    """

QUERY_FOR_ACTUAL_DEMAND = """
    SELECT CEIL(total_orders / (DATEDIFF(CONVERT_TZ(NOW(),'+00:00','+03:00'), datetime) / 30)) AS monthly_demand 
    FROM products
    WHERE id = {product_id}
    """

QUERY_FOR_PRICES = """
    SELECT
      CONVERT(value, CHAR) AS value 
    , min_quantity 
    , CONVERT(discount, CHAR) AS discount  
    , CONVERT(start_date, CHAR) AS start_date
    , CONVERT(end_date, CHAR) AS end_date
    FROM product_prices
    WHERE product_id = {}
        AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN start_date AND IFNULL(end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
    """

QUERY_FOR_SUPPLIER_INFO = """
    SELECT
    c.name
    , CONVERT(s.grade_average, CHAR) AS grade_average
    , (SELECT CONVERT(SUM(total_orders), CHAR)
    FROM products p2
    WHERE p2.supplier_id = p.supplier_id) AS total_deals
    , CASE 
        WHEN DATEDIFF(CONVERT_TZ(NOW(),'+00:00','+03:00'), u.datetime) < 365 THEN FLOOR(CEIL(DATEDIFF(CONVERT_TZ(NOW(),'+00:00','+03:00'), u.datetime) / 31))
        ELSE FLOOR(ROUND(DATEDIFF(CONVERT_TZ(NOW(),'+00:00','+03:00'), u.datetime) / 365))
    END value
    , CASE 
        WHEN u.datetime IS NULL THEN NULL
        WHEN DATEDIFF(CONVERT_TZ(NOW(),'+00:00','+03:00'), u.datetime) < 365 THEN 'months'
        ELSE 'years'
    END period
    FROM users u 
        JOIN suppliers s ON s.user_id = u.id
        JOIN products p ON p.supplier_id = s.id 
                                    AND p.id = {product_id}
        JOIN companies c ON c.supplier_id = s.id
    """

QUERY_FOR_REVIEWS = """
    SELECT pr.seller_id, pr.text, CONVERT(pr.grade_overall, CHAR) AS grade_overall, CONVERT(pr.datetime, CHAR) AS datetime, prp.image_url 
    FROM product_review_photos prp RIGHT JOIN product_reviews pr
    ON prp.product_review_id = pr.id
    WHERE pr.product_id = {product_id}
    ORDER BY pr.datetime DESC
    {quantity}
"""

QUERY_FOR_PRODUCT_GRADE = """
    SELECT 
      CONVERT(p.grade_average, CHAR) AS grade_average
    , COUNT(pr.id) AS count
    FROM products p
        LEFT JOIN product_reviews pr ON pr.product_id = p.id
    WHERE p.id = {}
    GROUP BY p.grade_average 
    """

QUERY_FOR_PRODUCT_GRADE_DETAILS = """
    SELECT 
      grade_overall 
    , COUNT(1) AS count
    FROM product_reviews pr 
    WHERE product_id = {}
    GROUP BY grade_overall
    ORDER BY grade_overall DESC
    """

QUERY_TO_GET_PROPERTIES = """
    SELECT cpt.name, cpv.value, cpv.optional_value
    FROM category_properties cp 
        JOIN category_property_types cpt ON cpt.id = cp.property_type_id
                                                    AND cp.category_id = {category_id}
        JOIN category_property_values cpv ON cpv.property_type_id = cpt.id
    """

QUERY_TO_GET_VARIATIONS = """
    SELECT cvt.name, cvv.value 
    FROM category_variations cv 
        JOIN category_variation_types cvt ON cvt.id = cv.variation_type_id
                                                    AND cv.category_id = {category_id}
        JOIN category_variation_values cvv ON cvv.variation_type_id = cvt.id 
    """

QUERY_ALL_CATEGORIES = """
    WITH RECURSIVE cte (id, name, parent_id) AS
    (
        SELECT id, name, parent_id
        FROM categories

        UNION ALL

        SELECT c.id, c.name, c.parent_id
        FROM categories c
            INNER JOIN cte
                ON c.parent_id = cte.id
    )
    SELECT *
    FROM cte
    """

QUERY_SUPPLIER_PRODUCTS = """
    WITH product_balance (prod_id, balance) AS (
        SELECT pvv.product_id, SUM(pvc.count)
        FROM product_variation_values pvv
            JOIN product_variation_counts pvc ON pvc.product_variation_value1_id = pvv.id 
        GROUP BY pvv.product_id 
    )
    SELECT 
    p.id
    , p.name 
    , pi.image_url
    , CONVERT(p.datetime, CHAR) AS datetime
    , p.with_discount
    , p.is_active 
    , CONVERT(pp.value, CHAR) AS price
    , pp.min_quantity 
    , CONVERT(IFNULL(pb.balance, 0), CHAR) AS balance
    , CONVERT(p.grade_average, CHAR) AS grade_average
    , p.total_orders
    FROM products p
        JOIN product_images pi ON pi.product_id = p.id
                            AND pi.serial_number = 0
        JOIN product_prices pp ON pp.product_id = p.id
                            AND CONVERT_TZ(CONVERT_TZ(NOW(),'+00:00','+03:00'),'+00:00','+03:00') BETWEEN pp.start_date AND IFNULL(pp.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
                            AND pp.min_quantity = (SELECT MIN(min_quantity)
                                                FROM product_prices pp2
                                                WHERE pp2.product_id = p.id
                                                    AND CONVERT_TZ(CONVERT_TZ(NOW(),'+00:00','+03:00'),'+00:00','+03:00') BETWEEN pp2.start_date AND IFNULL(pp2.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y')))
        LEFT JOIN product_balance pb ON pb.prod_id = p.id                                               
    WHERE p.supplier_id = {supplier_id}
    """