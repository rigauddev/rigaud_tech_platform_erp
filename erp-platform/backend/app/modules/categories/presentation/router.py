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
from app.modules.categories.application.use_cases import (
    ActivateCategory,
    CategoryCreateInput,
    CategoryListInput,
    CategoryUpdateInput,
    CreateCategory,
    DeactivateCategory,
    DeleteCategory,
    GetCategory,
    ListCategories,
    ReorderCategory,
    UpdateCategory,
)
from app.modules.categories.domain.entities import CategoryStatus
from app.modules.categories.domain.exceptions import (
    CategoryAlreadyExistsError,
    CategoryCycleError,
    CategoryError,
    CategoryInternalCodeAlreadyExistsError,
    CategoryInUseError,
    CategoryNotFoundError,
    CategorySlugAlreadyExistsError,
    InvalidCategoryDataError,
)
from app.modules.categories.infrastructure.models import CategoryModel
from app.modules.categories.infrastructure.repositories import SQLAlchemyCategoryRepository
from app.modules.categories.presentation.schemas import (
    CategoryCreateRequest,
    CategoryReorderRequest,
    CategoryResponse,
    CategoryTreeResponse,
    CategoryUpdateRequest,
)
from app.shared.api.responses import PaginationMeta, error_response, success_response

router = APIRouter(prefix="/categories", tags=["Categories"])
logger = logging.getLogger("application")
audit_logger = logging.getLogger("audit")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=100)]
StatusQuery = Annotated[CategoryStatus | None, Query()]
ParentQuery = Annotated[UUID | None, Query(alias="parent")]
SearchQuery = Annotated[str | None, Query(max_length=120)]
OrderingQuery = Annotated[str, Query(pattern="^(manual|name)$")]
TreeQuery = Annotated[bool, Query()]


def _category_response(category: CategoryModel) -> CategoryResponse:
    return CategoryResponse(
        id=category.id,
        tenant_id=category.tenant_id,
        parent_id=category.parent_id,
        internal_code=category.internal_code,
        name=category.name,
        slug=category.slug,
        description=category.description,
        icon=category.icon,
        color=category.color,
        display_order=category.display_order,
        status=category.status,
        is_active=category.is_active,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _category_tree_response(
    category: CategoryModel,
    children_by_parent: dict[UUID | None, list[CategoryModel]],
) -> CategoryTreeResponse:
    base = _category_response(category).model_dump()
    children = [
        _category_tree_response(child, children_by_parent)
        for child in children_by_parent.get(category.id, [])
    ]
    return CategoryTreeResponse(**base, children=children)


def _tree(items: list[CategoryModel]) -> list[CategoryTreeResponse]:
    children_by_parent: dict[UUID | None, list[CategoryModel]] = {}
    for category in items:
        children_by_parent.setdefault(category.parent_id, []).append(category)
    return [
        _category_tree_response(category, children_by_parent)
        for category in children_by_parent.get(None, [])
    ]


def _snapshot(category: CategoryModel) -> dict[str, str | int | bool | None]:
    return {
        "id": str(category.id),
        "tenant_id": str(category.tenant_id),
        "parent_id": str(category.parent_id) if category.parent_id else None,
        "internal_code": category.internal_code,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "icon": category.icon,
        "color": category.color,
        "display_order": category.display_order,
        "status": category.status.value,
        "is_active": category.is_active,
    }


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


async def _record_category_event(
    session: AsyncSession,
    *,
    event_name: str,
    action: str,
    category: CategoryModel,
    current_user: AuthenticatedUser,
    before_data: dict | None = None,
    after_data: dict | None = None,
) -> None:
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name=event_name,
            module="categories",
            action=action,
            entity_type="category",
            entity_id=category.id,
            tenant_id=category.tenant_id,
            actor_user_id=current_user.id,
            before_data=before_data,
            after_data=after_data,
        )
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    logger.info(
        "category.creation.started",
        extra={"event": "category.creation.started", "tenant_id": str(current_user.tenant_id)},
    )
    try:
        category = await CreateCategory(SQLAlchemyCategoryRepository(session)).execute(
            CategoryCreateInput(
                tenant_id=current_user.tenant_id,
                parent_id=payload.parent_id,
                internal_code=payload.internal_code,
                name=payload.name,
                slug=payload.slug,
                description=payload.description,
                icon=payload.icon,
                color=payload.color,
                display_order=payload.display_order,
                actor_id=current_user.id,
            )
        )
        audit_logger.info(
            "category.created",
            extra={
                "event": "category.created",
                "actor_id": str(current_user.id),
                "tenant_id": str(current_user.tenant_id),
                "category_id": str(category.id),
                "request_id": _request_id(request),
            },
        )
        await _record_category_event(
            session,
            event_name="category.created",
            action="created",
            category=category,
            current_user=current_user,
            after_data=_snapshot(category),
        )
        await session.commit()
        return success_response(
            "CATEGORY_CREATED",
            data=_category_response(category).model_dump(mode="json"),
        )
    except CategoryError as exc:
        await session.rollback()
        logger.warning("category.creation.failed", extra={"event": "category.creation.failed"})
        return category_exception_to_response(exc)


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    status: StatusQuery = None,
    parent: ParentQuery = None,
    search: SearchQuery = None,
    ordering: OrderingQuery = "manual",
    tree: TreeQuery = False,
) -> JSONResponse:
    result = await ListCategories(SQLAlchemyCategoryRepository(session)).execute(
        CategoryListInput(
            tenant_id=current_user.tenant_id,
            page=page,
            page_size=page_size,
            status=status,
            parent_id=parent,
            search=search,
            ordering=ordering,
            tree=tree,
        )
    )
    logger.info(
        "category.query.completed",
        extra={
            "event": "category.query.completed",
            "tenant_id": str(current_user.tenant_id),
            "total": result.total,
            "tree": tree,
        },
    )
    data = (
        [category.model_dump(mode="json") for category in _tree(result.items)]
        if tree
        else [_category_response(category).model_dump(mode="json") for category in result.items]
    )
    return success_response(
        "CATEGORY_LIST_RETRIEVED",
        data=data,
        meta=PaginationMeta.from_total(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        category = await GetCategory(SQLAlchemyCategoryRepository(session)).execute(
            category_id,
            tenant_id=current_user.tenant_id,
        )
        return success_response(
            "CATEGORY_RETRIEVED",
            data=_category_response(category).model_dump(mode="json"),
        )
    except CategoryError as exc:
        return category_exception_to_response(exc)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    repository = SQLAlchemyCategoryRepository(session)
    try:
        current = await GetCategory(repository).execute(
            category_id, tenant_id=current_user.tenant_id
        )
        before = _snapshot(current)
        category = await UpdateCategory(repository).execute(
            category_id,
            tenant_id=current_user.tenant_id,
            input_data=CategoryUpdateInput(
                parent_id=payload.parent_id,
                parent_id_provided="parent_id" in payload.model_fields_set,
                internal_code=payload.internal_code,
                name=payload.name,
                slug=payload.slug,
                description=payload.description,
                icon=payload.icon,
                color=payload.color,
                display_order=payload.display_order,
                actor_id=current_user.id,
            ),
        )
        await _record_category_event(
            session,
            event_name="category.updated",
            action="updated",
            category=category,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(category),
        )
        await session.commit()
        logger.info(
            "category.update.completed",
            extra={"event": "category.update.completed", "category_id": str(category.id)},
        )
        return success_response(
            "CATEGORY_UPDATED",
            data=_category_response(category).model_dump(mode="json"),
        )
    except CategoryError as exc:
        await session.rollback()
        return category_exception_to_response(exc)


@router.post("/{category_id}/activate", response_model=CategoryResponse)
async def activate_category(
    category_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_category_state(
        category_id,
        request,
        session,
        current_user,
        event_name="category.activated",
        action="activated",
        use_case=ActivateCategory,
    )


@router.post("/{category_id}/deactivate", response_model=CategoryResponse)
async def deactivate_category(
    category_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_category_state(
        category_id,
        request,
        session,
        current_user,
        event_name="category.deactivated",
        action="deactivated",
        use_case=DeactivateCategory,
    )


@router.post("/{category_id}/reorder", response_model=CategoryResponse)
async def reorder_category(
    category_id: UUID,
    payload: CategoryReorderRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    repository = SQLAlchemyCategoryRepository(session)
    try:
        current = await GetCategory(repository).execute(
            category_id, tenant_id=current_user.tenant_id
        )
        before = _snapshot(current)
        category = await ReorderCategory(repository).execute(
            category_id,
            tenant_id=current_user.tenant_id,
            display_order=payload.display_order,
            actor_id=current_user.id,
        )
        await _record_category_event(
            session,
            event_name="category.reordered",
            action="reordered",
            category=category,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(category),
        )
        await session.commit()
        audit_logger.info(
            "category.reordered",
            extra={
                "event": "category.reordered",
                "actor_id": str(current_user.id),
                "tenant_id": str(current_user.tenant_id),
                "category_id": str(category.id),
                "request_id": _request_id(request),
            },
        )
        return success_response(
            "CATEGORY_REORDERED",
            data=_category_response(category).model_dump(mode="json"),
        )
    except CategoryError as exc:
        await session.rollback()
        return category_exception_to_response(exc)


@router.delete("/{category_id}", response_model=CategoryResponse)
async def delete_category(
    category_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    repository = SQLAlchemyCategoryRepository(session)
    try:
        current = await GetCategory(repository).execute(
            category_id, tenant_id=current_user.tenant_id
        )
        before = _snapshot(current)
        category = await DeleteCategory(repository).execute(
            category_id,
            tenant_id=current_user.tenant_id,
            actor_id=current_user.id,
        )
        await _record_category_event(
            session,
            event_name="category.deleted",
            action="deleted",
            category=category,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(category),
        )
        await session.commit()
        audit_logger.info(
            "category.deleted",
            extra={
                "event": "category.deleted",
                "actor_id": str(current_user.id),
                "tenant_id": str(current_user.tenant_id),
                "category_id": str(category.id),
                "request_id": _request_id(request),
            },
        )
        return success_response(
            "CATEGORY_DELETED",
            data=_category_response(category).model_dump(mode="json"),
        )
    except CategoryError as exc:
        await session.rollback()
        return category_exception_to_response(exc)


async def _change_category_state(
    category_id: UUID,
    request: Request,
    session: AsyncSession,
    current_user: AuthenticatedUser,
    *,
    event_name: str,
    action: str,
    use_case,
) -> JSONResponse:
    repository = SQLAlchemyCategoryRepository(session)
    try:
        current = await GetCategory(repository).execute(
            category_id, tenant_id=current_user.tenant_id
        )
        before = _snapshot(current)
        category = await use_case(repository).execute(
            category_id,
            tenant_id=current_user.tenant_id,
            actor_id=current_user.id,
        )
        await _record_category_event(
            session,
            event_name=event_name,
            action=action,
            category=category,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(category),
        )
        await session.commit()
        audit_logger.info(
            event_name,
            extra={
                "event": event_name,
                "actor_id": str(current_user.id),
                "tenant_id": str(current_user.tenant_id),
                "category_id": str(category.id),
                "request_id": _request_id(request),
            },
        )
        return success_response(
            "CATEGORY_ACTIVATED" if action == "activated" else "CATEGORY_DEACTIVATED",
            data=_category_response(category).model_dump(mode="json"),
        )
    except CategoryError as exc:
        await session.rollback()
        return category_exception_to_response(exc)


def category_exception_to_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, CategoryNotFoundError):
        return error_response("CATEGORY_NOT_FOUND")
    if isinstance(exc, CategoryInternalCodeAlreadyExistsError):
        return error_response("CATEGORY_INTERNAL_CODE_ALREADY_EXISTS")
    if isinstance(exc, CategorySlugAlreadyExistsError):
        return error_response("CATEGORY_SLUG_ALREADY_EXISTS")
    if isinstance(exc, CategoryCycleError):
        return error_response("CATEGORY_CYCLE_DETECTED", status_code=status.HTTP_409_CONFLICT)
    if isinstance(exc, CategoryInUseError):
        return error_response("CATEGORY_IN_USE", status_code=status.HTTP_409_CONFLICT)
    if isinstance(exc, CategoryAlreadyExistsError):
        return error_response("CATEGORY_ALREADY_EXISTS")
    if isinstance(exc, InvalidCategoryDataError):
        return error_response("VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)
    return error_response("VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)
