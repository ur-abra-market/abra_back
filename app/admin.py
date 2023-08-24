from __future__ import annotations

from starlette_admin.contrib.sqla import Admin as SQLAlchemyAdmin
from starlette_admin.contrib.sqla import ModelView as SQLAlchemyModelView

from orm import (
    CategoryModel,
    CategoryToPropertyModel,
    CategoryToVariationTypeModel,
    CompanyImageModel,
    CompanyModel,
    CountryModel,
    NumberEmployeesModel,
    OrderModel,
    OrderProductVariationModel,
    OrderStatusModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductReviewModel,
    ProductReviewPhotoModel,
    ProductReviewReactionModel,
    ProductVariationCountModel,
    PropertyTypeModel,
    PropertyValueModel,
    PropertyValueToProductModel,
    ResetTokenModel,
    SellerAddressModel,
    SellerFavoriteModel,
    SellerImageModel,
    SellerModel,
    SellerNotificationsModel,
    SupplierModel,
    SupplierNotificationsModel,
    TagsModel,
    UserCredentialsModel,
    UserModel,
    UserSearchModel,
    VariationTypeModel,
    VariationValueModel,
    VariationValueToProductModel,
)
from orm.core import engine


def create_sqlalchemy_admin() -> SQLAlchemyAdmin:
    admin = SQLAlchemyAdmin(
        engine=engine,
        debug=False,
    )

    admin.add_view(SQLAlchemyModelView(CategoryModel))
    admin.add_view(SQLAlchemyModelView(CategoryToPropertyModel))
    admin.add_view(SQLAlchemyModelView(PropertyTypeModel))
    admin.add_view(SQLAlchemyModelView(PropertyValueModel))
    admin.add_view(SQLAlchemyModelView(CategoryToVariationTypeModel))
    admin.add_view(SQLAlchemyModelView(VariationTypeModel))
    admin.add_view(SQLAlchemyModelView(VariationValueModel))
    admin.add_view(SQLAlchemyModelView(CompanyModel))
    admin.add_view(SQLAlchemyModelView(CompanyImageModel))
    admin.add_view(SQLAlchemyModelView(NumberEmployeesModel))
    admin.add_view(SQLAlchemyModelView(CountryModel))
    admin.add_view(SQLAlchemyModelView(OrderModel))
    admin.add_view(SQLAlchemyModelView(OrderProductVariationModel))
    admin.add_view(SQLAlchemyModelView(OrderStatusModel))
    admin.add_view(SQLAlchemyModelView(ProductModel))
    admin.add_view(SQLAlchemyModelView(ProductImageModel))
    admin.add_view(SQLAlchemyModelView(ProductPriceModel))
    admin.add_view(SQLAlchemyModelView(PropertyValueToProductModel))
    admin.add_view(SQLAlchemyModelView(ProductReviewModel))
    admin.add_view(SQLAlchemyModelView(ProductReviewPhotoModel))
    admin.add_view(SQLAlchemyModelView(ProductReviewReactionModel))
    admin.add_view(SQLAlchemyModelView(ProductVariationCountModel))
    admin.add_view(SQLAlchemyModelView(VariationValueToProductModel))
    admin.add_view(SQLAlchemyModelView(ResetTokenModel))
    admin.add_view(SQLAlchemyModelView(SellerModel))
    admin.add_view(SQLAlchemyModelView(SellerAddressModel))
    admin.add_view(SQLAlchemyModelView(SellerFavoriteModel))
    admin.add_view(SQLAlchemyModelView(SellerImageModel))
    admin.add_view(SQLAlchemyModelView(SellerNotificationsModel))
    admin.add_view(SQLAlchemyModelView(SupplierModel))
    admin.add_view(SQLAlchemyModelView(SupplierNotificationsModel))
    admin.add_view(SQLAlchemyModelView(TagsModel))
    admin.add_view(SQLAlchemyModelView(UserModel))
    admin.add_view(SQLAlchemyModelView(UserCredentialsModel))
    admin.add_view(SQLAlchemyModelView(UserSearchModel))

    return admin
