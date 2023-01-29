QUERY_FOR_COMPILATION = """
    SELECT
      p.id
    , p.name
    , p.description
    , p.total_orders
    , CONVERT(p.grade_average, CHAR) AS grade_average
    , DATE_FORMAT(p.datetime, '%d/%m/%Y') AS date_added
    , (SELECT IF(SUM(discount) > 0, 1, 0)
       FROM product_prices pp1
       WHERE pp1.product_id = p.id
           AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp1.start_date AND IFNULL(pp1.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
        ) AS with_discount
    , FORMAT(pp.value * (1 - IFNULL(pp.discount, 0)), 2) AS price_include_discount
    , pp.min_quantity
    , pi.image_url
    , p.supplier_id
    FROM products p
        JOIN product_prices pp ON pp.product_id = p.id
                                           AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp.start_date AND IFNULL(pp.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
                                           AND pp.min_quantity = (SELECT MIN(min_quantity)
    								   		    			  FROM product_prices pp2
                                                              WHERE pp2.product_id = p.id
                                                                AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp2.start_date AND IFNULL(pp2.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y')))
        JOIN product_images pi ON pi.product_id = p.id
                                           AND pi.serial_number = 0
    WHERE p.category_id = {category_id}
        AND p.is_active = 1
    {where_clause}
    ORDER BY {order_by} DESC
    LIMIT {page_size}
    OFFSET {products_to_skip}
    """


QUERY_FOR_POPULAR_PRODUCTS = """
    SELECT
        p.id
        , p.name
        , p.description
        , p.total_orders
        , CONVERT(p.grade_average, CHAR) AS grade_average
        , DATE_FORMAT(p.`datetime`, '%d/%m/%Y') AS date_added
        , (
            SELECT IF(SUM(discount) > 0, 1, 0)
            FROM product_prices pp1
            WHERE pp1.product_id = p.id
            AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp1.start_date 
            AND IFNULL(pp1.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
          ) AS with_discount
        , FORMAT(pp.value * (1 - IFNULL(pp.discount, 0)), 2) AS price_include_discount
        , IFNULL(pp.min_quantity, 0) AS min_quantity
        , CONVERT(IFNULL(pp.value, 0), CHAR) AS value_price
        , {is_favorite_subquery} AS is_favorite
    --    , pi.image_url
    FROM products p
        JOIN product_prices pp ON pp.product_id = p.id
                                        AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp.start_date AND IFNULL(pp.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
                                        AND pp.min_quantity = (SELECT MIN(min_quantity)
                                    FROM product_prices pp2
                                                            WHERE pp2.product_id = p.id
                                                                AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp2.start_date AND IFNULL(pp2.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y')))
    --    JOIN product_images pi ON pi.product_id = p.id
    --                                    AND pi.serial_number = 0
    WHERE 
        p.id != {product_id}
        AND p.category_id = {category_id}
        AND p.is_active = 1
    ORDER BY {order_by} DESC
    LIMIT {page_size}
    OFFSET {products_to_skip}
"""


PRODUCT_IS_FAVORITE_SUBQUERY = """
    IFNULL((
        SELECT 1
        FROM seller_favorites sf 
        WHERE 
            sf.product_id = p.id
            AND sf.seller_id = {seller_id}
    ), 0)
"""


# in progress
QUERY_FOR_SIMILAR_PRODUCTS = """
    SELECT
      id
    , name
    , description
    , (SELECT IF(SUM(discount) > 0, 1, 0)
       FROM product_prices pp1
       WHERE pp1.product_id = p.id
           AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp1.start_date AND IFNULL(pp1.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
        ) AS with_discount
    FROM products p
    WHERE p.id != {product_id}
        AND p.category_id = {category_id}
        AND p.is_active = 1
    """

QUERY_FOR_CATEGORY_PATH = """
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
    """


QUERY_FOR_VARIATIONS = """
    SELECT
    cvt.name AS param
    , cvv.value AS value
    FROM product_variation_values pvv
        JOIN category_variation_values cvv ON cvv.id = pvv.variation_value_id
        JOIN category_variation_types cvt ON cvt.id = cvv.variation_type_id
    WHERE pvv.product_id = {}
    """


QUERY_FOR_PROPERTIES = """
    SELECT
    cpt.name AS param
    , cpv.value AS value
    FROM product_property_values ppv
        JOIN category_property_values cpv ON cpv.id = ppv.property_value_id
        JOIN category_property_types cpt ON cpt.id = cpv.property_type_id
    WHERE ppv.product_id = {}
    """


QUERY_FOR_COLORS = """
    SELECT cvv.value AS color
    FROM product_variation_values pvv
        JOIN category_variation_values cvv ON cvv.id = pvv.variation_value_id
        JOIN category_variation_types cvt ON cvt.id = cvv.variation_type_id
    WHERE pvv.product_id = {product_id}
        AND cvt.name = 'color'
    """


QUERY_FOR_SIZES = """
    SELECT cvv.value AS size
    FROM product_variation_values pvv
        JOIN category_variation_values cvv ON cvv.id = pvv.variation_value_id
        JOIN category_variation_types cvt ON cvt.id = cvv.variation_type_id
    WHERE pvv.product_id = {product_id}
        AND cvt.name = 'size'
    """


QUERY_FOR_CHECK_TOKEN = """
    SELECT *
    FROM reset_tokens
    WHERE status IS True
        AND reset_code = {}
    """


QUERY_FOR_PAGINATION_CTE_VARIATION = """
     variations_{type} AS (
	SELECT pvv.product_id
	FROM category_variation_values cvv
		JOIN product_variation_values pvv ON pvv.variation_value_id = cvv.id
                                                     AND cvv.variation_type_id = {variation_type_id}
                                                     AND cvv.value IN ({type_value})
    )
    """

QUERY_FOR_PAGINATION_CTE_PROPERTY = """
     properties_{type} AS (
	SELECT ppv.product_id
	FROM category_property_values cpv
		JOIN product_property_values ppv ON ppv.property_value_id = cpv.id
                                                     AND cpv.property_type_id = {property_type_id}
                                                     AND cpv.value IN ({type_value})
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
    , p.category_id
    , CONVERT(p.grade_average, CHAR) AS grade_average
    , CONVERT(IFNULL(pp.value, 0), CHAR) AS value_price
    , IFNULL(pp.min_quantity, 0) AS min_quantity
    , (SELECT IF(SUM(discount) > 0, 1, 0)
       FROM product_prices pp1
       WHERE pp1.product_id = p.id
           AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp1.start_date AND IFNULL(pp1.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
        ) AS with_discount
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

QUERY_FOR_MONTHLY_ACTUAL_DEMAND = """
    SELECT CEIL(total_orders / (DATEDIFF(CONVERT_TZ(NOW(),'+00:00','+03:00'), datetime) / 30)) AS monthly_demand
    FROM products
    WHERE id = {product_id}
    """

QUERY_FOR_DAILY_ACTUAL_DEMAND = """
    SELECT CEIL(total_orders / DATEDIFF(CONVERT_TZ(NOW(),'+00:00','+03:00'), datetime)) AS daily_demand
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
    SELECT
      p.id
    , p.name
    , pi.image_url
    , CONVERT(p.datetime, CHAR) AS datetime
    , (SELECT IF(SUM(discount) > 0, 1, 0)
       FROM product_prices pp1
       WHERE pp1.product_id = p.id
           AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp1.start_date AND IFNULL(pp1.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
        ) AS with_discount
    , p.is_active
    , CONVERT(pp.value, CHAR) AS price
    , pp.min_quantity
    , (SELECT CONVERT(IFNULL(SUM(pvc.count), 0), CHAR)
    FROM product_variation_values pvv
        JOIN product_variation_counts pvc ON pvc.product_variation_value1_id = pvv.id
                                            AND pvv.product_id = p.id
    ) AS balance
    , CONVERT(p.grade_average, CHAR) AS grade_average
    , p.total_orders
    FROM products p
        LEFT JOIN product_images pi ON pi.product_id = p.id
                            AND pi.serial_number = 0
        JOIN product_prices pp ON pp.product_id = p.id
                            AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp.start_date AND IFNULL(pp.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
                            AND pp.min_quantity = (SELECT MIN(min_quantity)
                                                FROM product_prices pp2
                                                WHERE pp2.product_id = p.id
                                                    AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp2.start_date AND IFNULL(pp2.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y')))
    WHERE p.supplier_id = {supplier_id}
    """

WHERE_CLAUSE_IS_ON_SALE = """
    EXISTS
    (SELECT 1 AS with_discount
    FROM product_prices pp1
    WHERE pp1.product_id = p.id
        AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN pp1.start_date AND IFNULL(pp1.end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
        AND pp1.discount > 0
    )
    """

# doesn't used now
QUERY_UPDATE_PRODUCT_PRICE = """
    UPDATE product_prices
    SET end_date = CONVERT_TZ(NOW(),'+00:00','+03:00')
    WHERE product_id = {product_id}
        AND min_quantity = {min_quantity}
        AND CONVERT_TZ(NOW(),'+00:00','+03:00') BETWEEN start_date AND IFNULL(end_date, STR_TO_DATE('01-01-2099', '%d-%m-%Y'))
"""

QUERY_IS_ALOWED_TO_REVIEW = """
    SELECT 1
    FROM order_product_variations opv
        JOIN orders o ON o.id = opv.order_id
                    AND o.seller_id = {seller_id}
                    AND opv.status_id = 0
        JOIN product_variation_counts pvc ON pvc.id = opv.product_variation_count_id
        JOIN product_variation_values pvv ON (pvv.id = pvc.product_variation_value1_id
                                        OR pvv.id = pvc.product_variation_value2_id)
                                        AND pvv.product_id = {product_id}
    LIMIT 1
"""


# QUERY_FOR_REACTIONS = """
#     SELECT COUNT(prr.)
# """