class RoleAlreadyExistsError(Exception):
    pass


class RoleNotFoundError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class CannotDeactivateSelfError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class UnitAlreadyExistsError(Exception):
    pass


class UnitNotFoundError(Exception):
    pass


class CategoryAlreadyExistsError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


class ProductAlreadyExistsError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class WarehouseAlreadyExistsError(Exception):
    pass


class WarehouseNotFoundError(Exception):
    pass


class ProductCannotBeProducedError(Exception):
    pass


class CustomerAlreadyExistsError(Exception):
    pass


class CustomerNotFoundError(Exception):
    pass


class DeliveryNotFoundError(Exception):
    pass


class CourierNotFoundError(Exception):
    pass


class InvalidCourierError(Exception):
    pass


class ProductCannotBeDeliveredError(Exception):
    pass


class ProductPriceNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class DuplicateDeliveryProductError(Exception):
    pass


class SupplierAlreadyExistsError(Exception):
    pass


class SupplierNotFoundError(Exception):
    pass


class PurchaseNotFoundError(Exception):
    pass


class PurchaseAlreadyExistsError(Exception):
    pass


class DuplicatePurchaseProductError(Exception):
    pass


class ProductCannotBePurchasedError(Exception):
    pass
