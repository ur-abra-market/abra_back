SQL_QUERY_FOR_CATEGORY_ID = '''
    SELECT id
    FROM web_platform.categories
    WHERE name = "{}"
    '''

SQL_QUERY_FOR_BESTSELLERS = '''
    WITH product_completed_orders(product_id, total)
    AS (
        SELECT product_id, SUM(count) as total
        FROM web_platform.orders
        WHERE is_completed = 1
        GROUP BY product_id
    )
    SELECT p.id, p.name, p.description, p.with_discount, FORMAT(pco.total, 0) AS total
    FROM web_platform.products p
        JOIN product_completed_orders pco ON pco.product_id = p.id
    WHERE p.category_id = {}
    ORDER BY pco.total DESC
    LIMIT 6
    '''

SQL_QUERY_FOR_NEW_ARRIVALS = '''
    SELECT id, name, description, DATE_FORMAT(datetime, '%d/%m/%Y') AS date
    FROM web_platform.products
    WHERE category_id = {}
    ORDER BY datetime DESC
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
    SELECT p.id, p.name, p.description, FORMAT(pr.rating, 2) AS rating
    FROM web_platform.products p
        JOIN product_ratings pr ON pr.product_id = p.id
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
    SELECT p.id, p.name, p.description, p.with_discount, FORMAT(pco.total, 0) AS total
    FROM web_platform.products p
        JOIN product_completed_orders pco ON pco.product_id = p.id
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
    SELECT p.id, p.name, p.description, FORMAT(pco.total, 0) AS total
    FROM web_platform.products p
        JOIN product_completed_orders pco ON pco.product_id = p.id
    WHERE p.category_id = {}
    ORDER BY pco.total DESC
    LIMIT 6
    '''