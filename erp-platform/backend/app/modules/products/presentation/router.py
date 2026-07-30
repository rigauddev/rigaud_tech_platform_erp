import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.modules.audit.application.service import AuditEventInput, AuditService
from app.modules.audit.infrastructure.repositories import SQLAlchemyAuditEventRepository
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.presentation.dependencies import get_current_user
from app.modules.products.application.use_cases import (
    ActivateProduct,
    ChangeProductAvailability,
    CreateProduct,
    DeactivateProduct,
    DeleteProduct,
    GetProduct,
    ListProducts,
    ProductCreateInput,
    ProductListInput,
    ProductUpdateInput,
    UpdateProduct,
)
from app.modules.products.domain.entities import ProductType, UnitOfMeasure
from app.modules.products.domain.exceptions import (
    InvalidProductDataError,
    ProductAlreadyExistsError,
    ProductError,
    ProductNotFoundError,
)
from app.modules.products.infrastructure.models import ProductModel
from app.modules.products.infrastructure.repositories import SQLAlchemyProductRepository
from app.modules.products.presentation.schemas import (
    ProductAvailabilityRequest,
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
)
from app.shared.api.responses import PaginationMeta, error_response, success_response

router = APIRouter(prefix="/products", tags=["Products"])
logger = logging.getLogger("application")
audit_logger = logging.getLogger("audit")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=100)]
ProductTypeQuery = Annotated[ProductType | None, Query(alias="product_type")]
UnitQuery = Annotated[UnitOfMeasure | None, Query(alias="unit_of_measure")]
IsActiveQuery = Annotated[bool | None, Query()]
AvailableQuery = Annotated[bool | None, Query(alias="is_available_for_sale")]
SearchQuery = Annotated[str | None, Query(max_length=120)]


def _product_response(product: ProductModel) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        tenant_id=product.tenant_id,
        name=product.name,
        description=product.description,
        internal_code=product.internal_code,
        barcode=product.barcode,
        product_type=product.product_type,
        unit_of_measure=product.unit_of_measure,
        sale_price=product.sale_price,
        cost_price=product.cost_price,
        main_image_url=product.main_image_url,
        is_active=product.is_active,
        is_available_for_sale=product.is_available_for_sale,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


def _snapshot(product: ProductModel) -> dict[str, str | bool | None]:
    return {
        "id": str(product.id),
        "tenant_id": str(product.tenant_id),
        "name": product.name,
        "internal_code": product.internal_code,
        "barcode": product.barcode,
        "product_type": product.product_type.value,
        "unit_of_measure": product.unit_of_measure.value,
        "sale_price": str(product.sale_price),
        "cost_price": str(product.cost_price),
        "main_image_url": product.main_image_url,
        "is_active": product.is_active,
        "is_available_for_sale": product.is_available_for_sale,
    }


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


async def _record_product_event(
    session: AsyncSession,
    *,
    event_name: str,
    action: str,
    product: ProductModel,
    current_user: AuthenticatedUser,
    before_data: dict | None = None,
    after_data: dict | None = None,
) -> None:
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name=event_name,
            module="products",
            action=action,
            entity_type="product",
            entity_id=product.id,
            tenant_id=product.tenant_id,
            actor_user_id=current_user.id,
            before_data=before_data,
            after_data=after_data,
        )
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    logger.info(
        "product.creation.started",
        extra={"event": "product.creation.started", "tenant_id": str(current_user.tenant_id)},
    )
    try:
        product = await CreateProduct(SQLAlchemyProductRepository(session)).execute(
            ProductCreateInput(
                tenant_id=current_user.tenant_id,
                name=payload.name,
                description=payload.description,
                internal_code=payload.internal_code,
                barcode=payload.barcode,
                product_type=payload.product_type,
                unit_of_measure=payload.unit_of_measure,
                sale_price=payload.sale_price,
                cost_price=payload.cost_price,
                main_image_url=payload.main_image_url,
                is_available_for_sale=payload.is_available_for_sale,
                actor_id=current_user.id,
            )
        )
        audit_logger.info(
            "product.created",
            extra={
                "event": "product.created",
                "actor_id": str(current_user.id),
                "tenant_id": str(current_user.tenant_id),
                "product_id": str(product.id),
                "request_id": _request_id(request),
            },
        )
        await _record_product_event(
            session,
            event_name="product.created",
            action="created",
            product=product,
            current_user=current_user,
            after_data=_snapshot(product),
        )
        await session.commit()
        logger.info(
            "product.creation.completed",
            extra={"event": "product.creation.completed", "product_id": str(product.id)},
        )
        return success_response(
            "PRODUCT_CREATED",
            data=_product_response(product).model_dump(mode="json"),
        )
    except ProductError as exc:
        await session.rollback()
        logger.warning("product.creation.failed", extra={"event": "product.creation.failed"})
        return product_exception_to_response(exc)


@router.get("", response_model=list[ProductResponse])
async def list_products(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    product_type: ProductTypeQuery = None,
    unit_of_measure: UnitQuery = None,
    is_active: IsActiveQuery = None,
    is_available_for_sale: AvailableQuery = None,
    search: SearchQuery = None,
) -> JSONResponse:
    result = await ListProducts(SQLAlchemyProductRepository(session)).execute(
        ProductListInput(
            tenant_id=current_user.tenant_id,
            page=page,
            page_size=page_size,
            product_type=product_type,
            unit_of_measure=unit_of_measure,
            is_active=is_active,
            is_available_for_sale=is_available_for_sale,
            search=search,
        )
    )
    logger.info(
        "product.query.completed",
        extra={
            "event": "product.query.completed",
            "tenant_id": str(current_user.tenant_id),
            "total": result.total,
        },
    )
    return success_response(
        "PRODUCTS_RETRIEVED",
        data=[_product_response(product).model_dump(mode="json") for product in result.items],
        meta=PaginationMeta.from_total(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        product = await GetProduct(SQLAlchemyProductRepository(session)).execute(
            product_id,
            tenant_id=current_user.tenant_id,
        )
        return success_response(
            "PRODUCT_RETRIEVED",
            data=_product_response(product).model_dump(mode="json"),
        )
    except ProductError as exc:
        return product_exception_to_response(exc)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    payload: ProductUpdateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    repository = SQLAlchemyProductRepository(session)
    try:
        current = await GetProduct(repository).execute(product_id, tenant_id=current_user.tenant_id)
        before = _snapshot(current)
        image_before = current.main_image_url
        product = await UpdateProduct(repository).execute(
            product_id,
            tenant_id=current_user.tenant_id,
            input_data=ProductUpdateInput(
                name=payload.name,
                description=payload.description,
                internal_code=payload.internal_code,
                barcode=payload.barcode,
                product_type=payload.product_type,
                unit_of_measure=payload.unit_of_measure,
                sale_price=payload.sale_price,
                cost_price=payload.cost_price,
                main_image_url=payload.main_image_url,
                is_available_for_sale=payload.is_available_for_sale,
                actor_id=current_user.id,
            ),
        )
        after = _snapshot(product)
        await _record_product_event(
            session,
            event_name="product.updated",
            action="updated",
            product=product,
            current_user=current_user,
            before_data=before,
            after_data=after,
        )
        if payload.main_image_url is not None and payload.main_image_url != image_before:
            await _record_product_event(
                session,
                event_name="product.image.changed",
                action="image_changed",
                product=product,
                current_user=current_user,
                before_data={"main_image_url": image_before},
                after_data={"main_image_url": product.main_image_url},
            )
        await session.commit()
        logger.info(
            "product.update.completed",
            extra={"event": "product.update.completed", "product_id": str(product.id)},
        )
        return success_response(
            "PRODUCT_UPDATED",
            data=_product_response(product).model_dump(mode="json"),
        )
    except ProductError as exc:
        await session.rollback()
        return product_exception_to_response(exc)


@router.post("/{product_id}/activate", response_model=ProductResponse)
async def activate_product(
    product_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_product_state(
        product_id,
        request,
        session,
        current_user,
        event_name="product.activated",
        action="activated",
        use_case=ActivateProduct,
    )


@router.post("/{product_id}/deactivate", response_model=ProductResponse)
async def deactivate_product(
    product_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_product_state(
        product_id,
        request,
        session,
        current_user,
        event_name="product.deactivated",
        action="deactivated",
        use_case=DeactivateProduct,
    )


@router.post("/{product_id}/availability", response_model=ProductResponse)
async def change_product_availability(
    product_id: UUID,
    payload: ProductAvailabilityRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    repository = SQLAlchemyProductRepository(session)
    try:
        current = await GetProduct(repository).execute(product_id, tenant_id=current_user.tenant_id)
        before = _snapshot(current)
        product = await ChangeProductAvailability(repository).execute(
            product_id,
            tenant_id=current_user.tenant_id,
            available=payload.is_available_for_sale,
            actor_id=current_user.id,
        )
        await _record_product_event(
            session,
            event_name="product.availability.changed",
            action="availability_changed",
            product=product,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(product),
        )
        await session.commit()
        return success_response(
            "PRODUCT_AVAILABILITY_CHANGED",
            data=_product_response(product).model_dump(mode="json"),
        )
    except ProductError as exc:
        await session.rollback()
        return product_exception_to_response(exc)


@router.delete("/{product_id}", response_model=ProductResponse)
async def delete_product(
    product_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    repository = SQLAlchemyProductRepository(session)
    try:
        current = await GetProduct(repository).execute(product_id, tenant_id=current_user.tenant_id)
        before = _snapshot(current)
        product = await DeleteProduct(repository).execute(
            product_id,
            tenant_id=current_user.tenant_id,
            actor_id=current_user.id,
        )
        await _record_product_event(
            session,
            event_name="product.deleted",
            action="deleted",
            product=product,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(product),
        )
        await session.commit()
        return success_response(
            "PRODUCT_DELETED",
            data=_product_response(product).model_dump(mode="json"),
        )
    except ProductError as exc:
        await session.rollback()
        return product_exception_to_response(exc)


async def _change_product_state(
    product_id: UUID,
    request: Request,
    session: AsyncSession,
    current_user: AuthenticatedUser,
    *,
    event_name: str,
    action: str,
    use_case,
) -> JSONResponse:
    repository = SQLAlchemyProductRepository(session)
    try:
        current = await GetProduct(repository).execute(product_id, tenant_id=current_user.tenant_id)
        before = _snapshot(current)
        product = await use_case(repository).execute(
            product_id,
            tenant_id=current_user.tenant_id,
            actor_id=current_user.id,
        )
        audit_logger.info(
            event_name,
            extra={
                "event": event_name,
                "actor_id": str(current_user.id),
                "tenant_id": str(current_user.tenant_id),
                "product_id": str(product.id),
                "request_id": _request_id(request),
            },
        )
        await _record_product_event(
            session,
            event_name=event_name,
            action=action,
            product=product,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(product),
        )
        await session.commit()
        return success_response(
            "PRODUCT_UPDATED",
            data=_product_response(product).model_dump(mode="json"),
        )
    except ProductError as exc:
        await session.rollback()
        return product_exception_to_response(exc)


def product_exception_to_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, ProductNotFoundError):
        return error_response("PRODUCT_NOT_FOUND")
    if isinstance(exc, ProductAlreadyExistsError):
        logger.warning(
            "product.uniqueness.conflict", extra={"event": "product.uniqueness.conflict"}
        )
        return error_response("PRODUCT_ALREADY_EXISTS")
    if isinstance(exc, InvalidProductDataError):
        return error_response("VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)
    return error_response("VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)
