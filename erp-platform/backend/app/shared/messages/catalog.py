from dataclasses import dataclass
from http import HTTPStatus
from typing import Final


@dataclass(frozen=True)
class MessageDefinition:
    code: str
    http_status: int
    client_message: str
    log_level: str = "info"
    audit_required: bool = False
    documentation_reference: str | None = None


MESSAGE_CATALOG: Final[dict[str, MessageDefinition]] = {
    "API_SUCCESS": MessageDefinition("API_SUCCESS", 200, "Operação concluída com sucesso."),
    "VALIDATION_ERROR": MessageDefinition(
        "VALIDATION_ERROR",
        422,
        "Existem dados inválidos na requisição.",
        "warning",
    ),
    "AUTH_INVALID_CREDENTIALS": MessageDefinition(
        "AUTH_INVALID_CREDENTIALS",
        401,
        "Credenciais inválidas.",
        "warning",
        True,
    ),
    "AUTH_TOKEN_INVALID": MessageDefinition(
        "AUTH_TOKEN_INVALID", 401, "Token inválido.", "warning"
    ),
    "AUTH_FORBIDDEN": MessageDefinition("AUTH_FORBIDDEN", 403, "Permissão negada.", "warning"),
    "AUTH_USER_INACTIVE": MessageDefinition(
        "AUTH_USER_INACTIVE", 403, "Usuário inativo.", "warning"
    ),
    "AUTH_USER_BLOCKED": MessageDefinition(
        "AUTH_USER_BLOCKED", 403, "Usuário bloqueado.", "warning", True
    ),
    "AUTH_MFA_STATUS_RETRIEVED": MessageDefinition(
        "AUTH_MFA_STATUS_RETRIEVED", 200, "Status da autenticação em dois fatores consultado."
    ),
    "AUTH_MFA_SETUP_STARTED": MessageDefinition(
        "AUTH_MFA_SETUP_STARTED", 200, "Configuração da autenticação em dois fatores iniciada."
    ),
    "AUTH_MFA_ENABLED": MessageDefinition(
        "AUTH_MFA_ENABLED", 200, "Autenticação em dois fatores habilitada.", audit_required=True
    ),
    "AUTH_MFA_DISABLED": MessageDefinition(
        "AUTH_MFA_DISABLED", 200, "Autenticação em dois fatores desabilitada.", audit_required=True
    ),
    "AUTH_MFA_REQUIRED": MessageDefinition(
        "AUTH_MFA_REQUIRED", 200, "Informe o código de verificação.", "info", True
    ),
    "AUTH_MFA_CHALLENGE_CREATED": MessageDefinition(
        "AUTH_MFA_CHALLENGE_CREATED", 200, "Desafio de autenticação criado."
    ),
    "AUTH_MFA_CODE_SENT": MessageDefinition(
        "AUTH_MFA_CODE_SENT", 200, "Código de verificação enviado."
    ),
    "AUTH_MFA_CODE_INVALID": MessageDefinition(
        "AUTH_MFA_CODE_INVALID", 401, "Código de verificação inválido.", "warning", True
    ),
    "AUTH_MFA_CODE_EXPIRED": MessageDefinition(
        "AUTH_MFA_CODE_EXPIRED", 401, "Código de verificação expirado.", "warning"
    ),
    "AUTH_MFA_CHALLENGE_EXPIRED": MessageDefinition(
        "AUTH_MFA_CHALLENGE_EXPIRED", 401, "Desafio de autenticação expirado.", "warning"
    ),
    "AUTH_MFA_CHALLENGE_LOCKED": MessageDefinition(
        "AUTH_MFA_CHALLENGE_LOCKED", 423, "Desafio de autenticação bloqueado.", "warning", True
    ),
    "AUTH_MFA_METHOD_NOT_FOUND": MessageDefinition(
        "AUTH_MFA_METHOD_NOT_FOUND", 404, "Método de autenticação não encontrado.", "warning"
    ),
    "AUTH_MFA_METHOD_NOT_ACTIVE": MessageDefinition(
        "AUTH_MFA_METHOD_NOT_ACTIVE", 409, "Método de autenticação não está ativo.", "warning"
    ),
    "AUTH_MFA_METHOD_ADDED": MessageDefinition(
        "AUTH_MFA_METHOD_ADDED", 200, "Método de autenticação adicionado.", audit_required=True
    ),
    "AUTH_MFA_METHOD_REMOVED": MessageDefinition(
        "AUTH_MFA_METHOD_REMOVED", 200, "Método de autenticação removido.", audit_required=True
    ),
    "AUTH_MFA_PRIMARY_METHOD_CHANGED": MessageDefinition(
        "AUTH_MFA_PRIMARY_METHOD_CHANGED",
        200,
        "Método principal atualizado.",
        audit_required=True,
    ),
    "AUTH_MFA_RECOVERY_CODES_GENERATED": MessageDefinition(
        "AUTH_MFA_RECOVERY_CODES_GENERATED",
        200,
        "Códigos de recuperação gerados.",
        audit_required=True,
    ),
    "AUTH_MFA_RECOVERY_CODE_INVALID": MessageDefinition(
        "AUTH_MFA_RECOVERY_CODE_INVALID", 401, "Código de recuperação inválido.", "warning"
    ),
    "AUTH_MFA_RECOVERY_CODE_USED": MessageDefinition(
        "AUTH_MFA_RECOVERY_CODE_USED", 200, "Código de recuperação utilizado.", audit_required=True
    ),
    "AUTH_MFA_RATE_LIMITED": MessageDefinition(
        "AUTH_MFA_RATE_LIMITED", 429, "Muitas tentativas. Aguarde e tente novamente.", "warning"
    ),
    "AUTH_MFA_PROVIDER_UNAVAILABLE": MessageDefinition(
        "AUTH_MFA_PROVIDER_UNAVAILABLE",
        503,
        "Serviço de verificação temporariamente indisponível.",
        "error",
    ),
    "AUTH_MFA_TOTP_INVALID": MessageDefinition(
        "AUTH_MFA_TOTP_INVALID", 401, "Código do aplicativo autenticador inválido.", "warning"
    ),
    "AUTH_MFA_ALREADY_ENABLED": MessageDefinition(
        "AUTH_MFA_ALREADY_ENABLED", 409, "Autenticação em dois fatores já habilitada.", "warning"
    ),
    "AUTH_MFA_NOT_ENABLED": MessageDefinition(
        "AUTH_MFA_NOT_ENABLED", 409, "Autenticação em dois fatores não habilitada.", "warning"
    ),
    "COMPANY_CREATED": MessageDefinition(
        "COMPANY_CREATED", 201, "Empresa criada com sucesso.", audit_required=True
    ),
    "COMPANY_UPDATED": MessageDefinition(
        "COMPANY_UPDATED", 200, "Empresa atualizada com sucesso.", audit_required=True
    ),
    "COMPANY_NOT_FOUND": MessageDefinition(
        "COMPANY_NOT_FOUND", 404, "Empresa não encontrada.", "warning"
    ),
    "COMPANY_ALREADY_EXISTS": MessageDefinition(
        "COMPANY_ALREADY_EXISTS", 409, "Empresa já cadastrada.", "warning"
    ),
    "BRANCH_CREATED": MessageDefinition(
        "BRANCH_CREATED", 201, "Filial criada com sucesso.", audit_required=True
    ),
    "BRANCH_LIST_RETRIEVED": MessageDefinition(
        "BRANCH_LIST_RETRIEVED", 200, "Filiais consultadas com sucesso."
    ),
    "BRANCH_NOT_FOUND": MessageDefinition(
        "BRANCH_NOT_FOUND", 404, "Filial não encontrada.", "warning"
    ),
    "BRANCH_ALREADY_EXISTS": MessageDefinition(
        "BRANCH_ALREADY_EXISTS", 409, "Filial já cadastrada.", "warning"
    ),
    "BRANCH_HEADQUARTERS_ALREADY_EXISTS": MessageDefinition(
        "BRANCH_HEADQUARTERS_ALREADY_EXISTS",
        409,
        "Esta empresa já possui matriz principal.",
        "warning",
    ),
    "CONTEXT_RETRIEVED": MessageDefinition(
        "CONTEXT_RETRIEVED", 200, "Contexto de acesso consultado com sucesso."
    ),
    "CONTEXT_SWITCHED": MessageDefinition(
        "CONTEXT_SWITCHED", 200, "Contexto de acesso atualizado.", audit_required=True
    ),
    "CONTEXT_NOT_ALLOWED": MessageDefinition(
        "CONTEXT_NOT_ALLOWED", 403, "Contexto de acesso não permitido.", "warning"
    ),
    "USER_CREATED": MessageDefinition(
        "USER_CREATED", 201, "Usuário criado com sucesso.", audit_required=True
    ),
    "USER_UPDATED": MessageDefinition(
        "USER_UPDATED", 200, "Usuário atualizado com sucesso.", audit_required=True
    ),
    "USER_NOT_FOUND": MessageDefinition(
        "USER_NOT_FOUND", 404, "Usuário não encontrado.", "warning"
    ),
    "USER_EMAIL_ALREADY_EXISTS": MessageDefinition(
        "USER_EMAIL_ALREADY_EXISTS",
        409,
        "E-mail já existe nesta empresa.",
        "warning",
    ),
    "USER_PASSWORD_CHANGED": MessageDefinition(
        "USER_PASSWORD_CHANGED",
        200,
        "Senha alterada. Faça login novamente.",
        audit_required=True,
    ),
    "USER_PASSWORD_RESET": MessageDefinition(
        "USER_PASSWORD_RESET",
        200,
        "Senha temporária definida. Usuário deve trocar a senha.",
        audit_required=True,
    ),
    "PRODUCT_CREATED": MessageDefinition(
        "PRODUCT_CREATED", 201, "Produto criado com sucesso.", audit_required=True
    ),
    "PRODUCT_UPDATED": MessageDefinition(
        "PRODUCT_UPDATED", 200, "Produto atualizado com sucesso.", audit_required=True
    ),
    "PRODUCT_ACTIVATED": MessageDefinition(
        "PRODUCT_ACTIVATED", 200, "Produto ativado com sucesso.", audit_required=True
    ),
    "PRODUCT_DEACTIVATED": MessageDefinition(
        "PRODUCT_DEACTIVATED", 200, "Produto desativado com sucesso.", audit_required=True
    ),
    "PRODUCT_DELETED": MessageDefinition(
        "PRODUCT_DELETED", 200, "Produto removido com sucesso.", audit_required=True
    ),
    "PRODUCT_RETRIEVED": MessageDefinition(
        "PRODUCT_RETRIEVED", 200, "Produto consultado com sucesso."
    ),
    "PRODUCT_LIST_RETRIEVED": MessageDefinition(
        "PRODUCT_LIST_RETRIEVED", 200, "Produtos consultados com sucesso."
    ),
    "PRODUCT_AVAILABILITY_UPDATED": MessageDefinition(
        "PRODUCT_AVAILABILITY_UPDATED",
        200,
        "Disponibilidade do produto atualizada.",
        audit_required=True,
    ),
    "PRODUCT_NOT_FOUND": MessageDefinition(
        "PRODUCT_NOT_FOUND", 404, "Produto não encontrado.", "warning"
    ),
    "PRODUCT_INTERNAL_CODE_ALREADY_EXISTS": MessageDefinition(
        "PRODUCT_INTERNAL_CODE_ALREADY_EXISTS",
        409,
        "Código interno já cadastrado nesta empresa.",
        "warning",
    ),
    "PRODUCT_BARCODE_ALREADY_EXISTS": MessageDefinition(
        "PRODUCT_BARCODE_ALREADY_EXISTS",
        409,
        "Código de barras já cadastrado nesta empresa.",
        "warning",
    ),
    "PRODUCT_INVALID_PRICE": MessageDefinition(
        "PRODUCT_INVALID_PRICE", 400, "Preço de venda inválido.", "warning"
    ),
    "PRODUCT_INVALID_COST": MessageDefinition(
        "PRODUCT_INVALID_COST", 400, "Custo inválido.", "warning"
    ),
    "PRODUCT_INVALID_TYPE": MessageDefinition(
        "PRODUCT_INVALID_TYPE", 400, "Tipo de produto inválido.", "warning"
    ),
    "PRODUCT_INVALID_UNIT": MessageDefinition(
        "PRODUCT_INVALID_UNIT", 400, "Unidade de medida inválida.", "warning"
    ),
    "PRODUCT_IMAGE_INVALID": MessageDefinition(
        "PRODUCT_IMAGE_INVALID", 400, "Imagem principal inválida.", "warning"
    ),
    "PRODUCT_IMAGE_TOO_LARGE": MessageDefinition(
        "PRODUCT_IMAGE_TOO_LARGE", 413, "Imagem principal excede o tamanho permitido.", "warning"
    ),
    "PRODUCT_NOT_AVAILABLE": MessageDefinition(
        "PRODUCT_NOT_AVAILABLE", 409, "Produto indisponível para venda.", "warning"
    ),
    "CATEGORY_CREATED": MessageDefinition(
        "CATEGORY_CREATED", 201, "Categoria criada com sucesso.", audit_required=True
    ),
    "CATEGORY_UPDATED": MessageDefinition(
        "CATEGORY_UPDATED", 200, "Categoria atualizada com sucesso.", audit_required=True
    ),
    "CATEGORY_ACTIVATED": MessageDefinition(
        "CATEGORY_ACTIVATED", 200, "Categoria ativada com sucesso.", audit_required=True
    ),
    "CATEGORY_DEACTIVATED": MessageDefinition(
        "CATEGORY_DEACTIVATED", 200, "Categoria desativada com sucesso.", audit_required=True
    ),
    "CATEGORY_REORDERED": MessageDefinition(
        "CATEGORY_REORDERED", 200, "Categoria reordenada com sucesso.", audit_required=True
    ),
    "CATEGORY_DELETED": MessageDefinition(
        "CATEGORY_DELETED", 200, "Categoria removida com sucesso.", audit_required=True
    ),
    "CATEGORY_RETRIEVED": MessageDefinition(
        "CATEGORY_RETRIEVED", 200, "Categoria consultada com sucesso."
    ),
    "CATEGORY_LIST_RETRIEVED": MessageDefinition(
        "CATEGORY_LIST_RETRIEVED", 200, "Categorias consultadas com sucesso."
    ),
    "CATEGORY_NOT_FOUND": MessageDefinition(
        "CATEGORY_NOT_FOUND", 404, "Categoria não encontrada.", "warning"
    ),
    "CATEGORY_ALREADY_EXISTS": MessageDefinition(
        "CATEGORY_ALREADY_EXISTS", 409, "Categoria já cadastrada.", "warning"
    ),
    "CATEGORY_INTERNAL_CODE_ALREADY_EXISTS": MessageDefinition(
        "CATEGORY_INTERNAL_CODE_ALREADY_EXISTS",
        409,
        "Código interno já cadastrado nesta empresa.",
        "warning",
    ),
    "CATEGORY_SLUG_ALREADY_EXISTS": MessageDefinition(
        "CATEGORY_SLUG_ALREADY_EXISTS",
        409,
        "Slug já cadastrado nesta empresa.",
        "warning",
    ),
    "CATEGORY_CYCLE_DETECTED": MessageDefinition(
        "CATEGORY_CYCLE_DETECTED",
        409,
        "A hierarquia da categoria não pode criar ciclos.",
        "warning",
    ),
    "CATEGORY_IN_USE": MessageDefinition(
        "CATEGORY_IN_USE",
        409,
        "Categoria em uso não pode ser removida.",
        "warning",
    ),
    "INVENTORY_BALANCE_LIST_RETRIEVED": MessageDefinition(
        "INVENTORY_BALANCE_LIST_RETRIEVED",
        200,
        "Saldos de estoque consultados com sucesso.",
    ),
    "INVENTORY_MOVEMENT_LIST_RETRIEVED": MessageDefinition(
        "INVENTORY_MOVEMENT_LIST_RETRIEVED",
        200,
        "Movimentações de estoque consultadas com sucesso.",
    ),
    "INVENTORY_ADJUSTMENT_CREATED": MessageDefinition(
        "INVENTORY_ADJUSTMENT_CREATED",
        200,
        "Ajuste de estoque registrado com sucesso.",
        audit_required=True,
    ),
    "INVENTORY_RESERVATION_CREATED": MessageDefinition(
        "INVENTORY_RESERVATION_CREATED",
        200,
        "Reserva de estoque registrada com sucesso.",
        audit_required=True,
    ),
    "INVENTORY_RESERVATION_RELEASED": MessageDefinition(
        "INVENTORY_RESERVATION_RELEASED",
        200,
        "Reserva de estoque liberada com sucesso.",
        audit_required=True,
    ),
    "INVENTORY_BALANCE_NOT_FOUND": MessageDefinition(
        "INVENTORY_BALANCE_NOT_FOUND",
        404,
        "Saldo de estoque não encontrado.",
        "warning",
    ),
    "INVENTORY_RESERVATION_NOT_FOUND": MessageDefinition(
        "INVENTORY_RESERVATION_NOT_FOUND",
        404,
        "Reserva de estoque não encontrada.",
        "warning",
    ),
    "INVENTORY_RESERVATION_INACTIVE": MessageDefinition(
        "INVENTORY_RESERVATION_INACTIVE",
        409,
        "Reserva de estoque não está ativa.",
        "warning",
    ),
    "INVENTORY_INSUFFICIENT_STOCK": MessageDefinition(
        "INVENTORY_INSUFFICIENT_STOCK",
        409,
        "Saldo disponível insuficiente.",
        "warning",
    ),
    "INVENTORY_INVALID_QUANTITY": MessageDefinition(
        "INVENTORY_INVALID_QUANTITY",
        400,
        "Quantidade de estoque inválida.",
        "warning",
    ),
    "INVENTORY_BRANCH_REQUIRED": MessageDefinition(
        "INVENTORY_BRANCH_REQUIRED",
        409,
        "Filial ativa obrigatória para movimentar estoque.",
        "warning",
    ),
    "WAREHOUSE_CREATED": MessageDefinition(
        "WAREHOUSE_CREATED", 201, "Depósito criado com sucesso.", audit_required=True
    ),
    "WAREHOUSE_UPDATED": MessageDefinition(
        "WAREHOUSE_UPDATED", 200, "Depósito atualizado com sucesso.", audit_required=True
    ),
    "WAREHOUSE_DELETED": MessageDefinition(
        "WAREHOUSE_DELETED", 200, "Depósito removido com sucesso.", audit_required=True
    ),
    "WAREHOUSE_DEFAULT_SET": MessageDefinition(
        "WAREHOUSE_DEFAULT_SET",
        200,
        "Depósito padrão atualizado com sucesso.",
        audit_required=True,
    ),
    "WAREHOUSE_RETRIEVED": MessageDefinition(
        "WAREHOUSE_RETRIEVED", 200, "Depósito consultado com sucesso."
    ),
    "WAREHOUSE_LIST_RETRIEVED": MessageDefinition(
        "WAREHOUSE_LIST_RETRIEVED", 200, "Depósitos consultados com sucesso."
    ),
    "WAREHOUSE_NOT_FOUND": MessageDefinition(
        "WAREHOUSE_NOT_FOUND", 404, "Depósito não encontrado.", "warning"
    ),
    "WAREHOUSE_CODE_ALREADY_EXISTS": MessageDefinition(
        "WAREHOUSE_CODE_ALREADY_EXISTS",
        409,
        "Código de depósito já cadastrado nesta filial.",
        "warning",
    ),
    "WAREHOUSE_BRANCH_REQUIRED": MessageDefinition(
        "WAREHOUSE_BRANCH_REQUIRED",
        409,
        "Filial ativa obrigatória para cadastrar depósito.",
        "warning",
    ),
    "WAREHOUSE_INVALID_DATA": MessageDefinition(
        "WAREHOUSE_INVALID_DATA", 400, "Dados do depósito inválidos.", "warning"
    ),
    "WAREHOUSE_INACTIVE": MessageDefinition(
        "WAREHOUSE_INACTIVE", 409, "Depósito inativo não aceita novas zonas.", "warning"
    ),
    "WAREHOUSE_ZONE_CREATED": MessageDefinition(
        "WAREHOUSE_ZONE_CREATED", 201, "Zona criada com sucesso.", audit_required=True
    ),
    "WAREHOUSE_ZONE_UPDATED": MessageDefinition(
        "WAREHOUSE_ZONE_UPDATED", 200, "Zona atualizada com sucesso.", audit_required=True
    ),
    "WAREHOUSE_ZONE_DELETED": MessageDefinition(
        "WAREHOUSE_ZONE_DELETED", 200, "Zona removida com sucesso.", audit_required=True
    ),
    "WAREHOUSE_ZONE_REORDERED": MessageDefinition(
        "WAREHOUSE_ZONE_REORDERED", 200, "Ordenação da zona atualizada.", audit_required=True
    ),
    "WAREHOUSE_ZONE_RETRIEVED": MessageDefinition(
        "WAREHOUSE_ZONE_RETRIEVED", 200, "Zona consultada com sucesso."
    ),
    "WAREHOUSE_ZONE_LIST_RETRIEVED": MessageDefinition(
        "WAREHOUSE_ZONE_LIST_RETRIEVED", 200, "Zonas consultadas com sucesso."
    ),
    "WAREHOUSE_ZONE_NOT_FOUND": MessageDefinition(
        "WAREHOUSE_ZONE_NOT_FOUND", 404, "Zona não encontrada.", "warning"
    ),
    "WAREHOUSE_ZONE_CODE_ALREADY_EXISTS": MessageDefinition(
        "WAREHOUSE_ZONE_CODE_ALREADY_EXISTS",
        409,
        "Código de zona já cadastrado neste depósito.",
        "warning",
    ),
    "WAREHOUSE_ZONE_BRANCH_REQUIRED": MessageDefinition(
        "WAREHOUSE_ZONE_BRANCH_REQUIRED",
        409,
        "Filial ativa obrigatória para cadastrar zona.",
        "warning",
    ),
    "WAREHOUSE_ZONE_INVALID_DATA": MessageDefinition(
        "WAREHOUSE_ZONE_INVALID_DATA", 400, "Dados da zona inválidos.", "warning"
    ),
    "WAREHOUSE_ZONE_INACTIVE": MessageDefinition(
        "WAREHOUSE_ZONE_INACTIVE", 409, "Zona inativa não aceita novas localizações.", "warning"
    ),
    "WAREHOUSE_LOCATION_CREATED": MessageDefinition(
        "WAREHOUSE_LOCATION_CREATED",
        201,
        "Localização criada com sucesso.",
        audit_required=True,
    ),
    "WAREHOUSE_LOCATION_UPDATED": MessageDefinition(
        "WAREHOUSE_LOCATION_UPDATED",
        200,
        "Localização atualizada com sucesso.",
        audit_required=True,
    ),
    "WAREHOUSE_LOCATION_ACTIVATED": MessageDefinition(
        "WAREHOUSE_LOCATION_ACTIVATED",
        200,
        "Localização ativada com sucesso.",
        audit_required=True,
    ),
    "WAREHOUSE_LOCATION_DEACTIVATED": MessageDefinition(
        "WAREHOUSE_LOCATION_DEACTIVATED",
        200,
        "Localização inativada com sucesso.",
        audit_required=True,
    ),
    "WAREHOUSE_LOCATION_DELETED": MessageDefinition(
        "WAREHOUSE_LOCATION_DELETED",
        200,
        "Localização removida com sucesso.",
        audit_required=True,
    ),
    "WAREHOUSE_LOCATION_REORDERED": MessageDefinition(
        "WAREHOUSE_LOCATION_REORDERED",
        200,
        "Ordenação da localização atualizada.",
        audit_required=True,
    ),
    "WAREHOUSE_LOCATION_RETRIEVED": MessageDefinition(
        "WAREHOUSE_LOCATION_RETRIEVED", 200, "Localização consultada com sucesso."
    ),
    "WAREHOUSE_LOCATION_LIST_RETRIEVED": MessageDefinition(
        "WAREHOUSE_LOCATION_LIST_RETRIEVED", 200, "Localizações consultadas com sucesso."
    ),
    "WAREHOUSE_LOCATION_NOT_FOUND": MessageDefinition(
        "WAREHOUSE_LOCATION_NOT_FOUND", 404, "Localização não encontrada.", "warning"
    ),
    "WAREHOUSE_LOCATION_CODE_ALREADY_EXISTS": MessageDefinition(
        "WAREHOUSE_LOCATION_CODE_ALREADY_EXISTS",
        409,
        "Código de localização já cadastrado neste depósito.",
        "warning",
    ),
    "WAREHOUSE_LOCATION_BARCODE_ALREADY_EXISTS": MessageDefinition(
        "WAREHOUSE_LOCATION_BARCODE_ALREADY_EXISTS",
        409,
        "Código de barras já cadastrado em outra localização.",
        "warning",
    ),
    "WAREHOUSE_LOCATION_QR_CODE_ALREADY_EXISTS": MessageDefinition(
        "WAREHOUSE_LOCATION_QR_CODE_ALREADY_EXISTS",
        409,
        "QR Code já cadastrado em outra localização.",
        "warning",
    ),
    "WAREHOUSE_LOCATION_BRANCH_REQUIRED": MessageDefinition(
        "WAREHOUSE_LOCATION_BRANCH_REQUIRED",
        409,
        "Filial ativa obrigatória para cadastrar localização.",
        "warning",
    ),
    "WAREHOUSE_LOCATION_INVALID_DATA": MessageDefinition(
        "WAREHOUSE_LOCATION_INVALID_DATA", 400, "Dados da localização inválidos.", "warning"
    ),
    "RECEIVING_DOCUMENT_CREATED": MessageDefinition(
        "RECEIVING_DOCUMENT_CREATED",
        201,
        "Documento de recebimento criado com sucesso.",
        audit_required=True,
    ),
    "RECEIVING_DOCUMENT_UPDATED": MessageDefinition(
        "RECEIVING_DOCUMENT_UPDATED",
        200,
        "Documento de recebimento atualizado com sucesso.",
        audit_required=True,
    ),
    "RECEIVING_DOCUMENT_STATUS_CHANGED": MessageDefinition(
        "RECEIVING_DOCUMENT_STATUS_CHANGED",
        200,
        "Status do recebimento atualizado.",
        audit_required=True,
    ),
    "RECEIVING_DOCUMENT_DELETED": MessageDefinition(
        "RECEIVING_DOCUMENT_DELETED",
        200,
        "Documento de recebimento removido com sucesso.",
        audit_required=True,
    ),
    "RECEIVING_DOCUMENT_RETRIEVED": MessageDefinition(
        "RECEIVING_DOCUMENT_RETRIEVED", 200, "Recebimento consultado com sucesso."
    ),
    "RECEIVING_DOCUMENT_LIST_RETRIEVED": MessageDefinition(
        "RECEIVING_DOCUMENT_LIST_RETRIEVED", 200, "Recebimentos consultados com sucesso."
    ),
    "RECEIVING_DOCUMENT_NOT_FOUND": MessageDefinition(
        "RECEIVING_DOCUMENT_NOT_FOUND", 404, "Recebimento não encontrado.", "warning"
    ),
    "RECEIVING_DOCUMENT_NUMBER_ALREADY_EXISTS": MessageDefinition(
        "RECEIVING_DOCUMENT_NUMBER_ALREADY_EXISTS",
        409,
        "Número de documento já cadastrado nesta filial.",
        "warning",
    ),
    "RECEIVING_DOCUMENT_BRANCH_REQUIRED": MessageDefinition(
        "RECEIVING_DOCUMENT_BRANCH_REQUIRED",
        409,
        "Filial ativa obrigatória para cadastrar recebimento.",
        "warning",
    ),
    "RECEIVING_DOCUMENT_INVALID_DATA": MessageDefinition(
        "RECEIVING_DOCUMENT_INVALID_DATA", 400, "Dados do recebimento inválidos.", "warning"
    ),
    "RECEIVING_DOCUMENT_ITEM_REQUIRED": MessageDefinition(
        "RECEIVING_DOCUMENT_ITEM_REQUIRED",
        400,
        "Recebimento deve possuir pelo menos um item.",
        "warning",
    ),
    "AUDIT_EVENTS_RETRIEVED": MessageDefinition(
        "AUDIT_EVENTS_RETRIEVED",
        200,
        "Eventos de auditoria consultados com sucesso.",
    ),
    "AUDIT_EVENT_RETRIEVED": MessageDefinition(
        "AUDIT_EVENT_RETRIEVED",
        200,
        "Evento de auditoria consultado com sucesso.",
    ),
    "AUDIT_EVENT_NOT_FOUND": MessageDefinition(
        "AUDIT_EVENT_NOT_FOUND", 404, "Evento de auditoria não encontrado.", "warning"
    ),
    "DEMO_STATUS_RETRIEVED": MessageDefinition(
        "DEMO_STATUS_RETRIEVED", 200, "Status do ambiente demo consultado."
    ),
    "DEMO_INSTALLED": MessageDefinition(
        "DEMO_INSTALLED", 200, "Ambiente demo instalado com sucesso."
    ),
    "DEMO_RESET": MessageDefinition("DEMO_RESET", 200, "Ambiente demo resetado com sucesso."),
    "DEMO_SCENARIOS_RETRIEVED": MessageDefinition(
        "DEMO_SCENARIOS_RETRIEVED", 200, "Cenários demo consultados com sucesso."
    ),
    "DEMO_NOT_AVAILABLE": MessageDefinition(
        "DEMO_NOT_AVAILABLE", 404, "Demo Environment indisponível neste ambiente.", "warning"
    ),
    "INTERNAL_SERVER_ERROR": MessageDefinition(
        "INTERNAL_SERVER_ERROR",
        HTTPStatus.INTERNAL_SERVER_ERROR,
        "Ocorreu um erro interno. Tente novamente.",
        "error",
    ),
    "SERVICE_UNAVAILABLE": MessageDefinition(
        "SERVICE_UNAVAILABLE", 503, "Serviço temporariamente indisponível.", "error"
    ),
}


def get_message(code: str) -> MessageDefinition:
    return MESSAGE_CATALOG.get(code) or MESSAGE_CATALOG["INTERNAL_SERVER_ERROR"]
