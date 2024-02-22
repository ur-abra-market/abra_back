from sqlalchemy import and_, event, func, select
from sqlalchemy.orm import aliased, join

from .product import ProductModel
from .product_prices import ProductPriceModel


def get_product_prices_by_func(aggr_func, field_name: str) -> ProductPriceModel:
    price = (ProductPriceModel.value - ProductPriceModel.value * ProductPriceModel.discount).label(
        "price"
    )
    subquery = (
        select(ProductPriceModel.product_id, aggr_func(price).label(field_name))
        .group_by(ProductPriceModel.product_id)
        .subquery()
    )
    price_join = join(
        ProductPriceModel,
        subquery,
        and_(
            ProductPriceModel.product_id == subquery.c.product_id,
            price == getattr(subquery.c, field_name),
        ),
    )
    price_alias = aliased(ProductPriceModel, price_join, flat=True)
    return price_alias


@event.listens_for(ProductModel, "before_mapper_configured")
def configure_product_prices_relationship(mapper, cls):
    from orm.product import product

    product.min_prices = get_product_prices_by_func(func.min, "min_price")
    product.max_prices = get_product_prices_by_func(func.max, "max_price")
