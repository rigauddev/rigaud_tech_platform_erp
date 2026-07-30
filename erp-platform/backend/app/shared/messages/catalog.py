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
    "PLAN_CREATED": MessageDefinition(
        "PLAN_CREATED", 201, "Plano criado com sucesso.", audit_required=True
    ),
    "PLAN_LIST_RETRIEVED": MessageDefinition(
        "PLAN_LIST_RETRIEVED", 200, "Planos consultados com sucesso."
    ),
    "PLAN_NOT_FOUND": MessageDefinition("PLAN_NOT_FOUND", 404, "Plano não encontrado.", "warning"),
    "PLAN_ALREADY_EXISTS": MessageDefinition(
        "PLAN_ALREADY_EXISTS", 409, "Plano já cadastrado.", "warning"
    ),
    "PLAN_INACTIVE": MessageDefinition("PLAN_INACTIVE", 409, "Plano inativo.", "warning"),
    "SUBSCRIPTION_CREATED": MessageDefinition(
        "SUBSCRIPTION_CREATED", 200, "Assinatura criada com sucesso.", audit_required=True
    ),
    "SUBSCRIPTION_RETRIEVED": MessageDefinition(
        "SUBSCRIPTION_RETRIEVED", 200, "Assinatura consultada com sucesso."
    ),
    "SUBSCRIPTION_PLAN_CHANGED": MessageDefinition(
        "SUBSCRIPTION_PLAN_CHANGED", 200, "Plano da assinatura alterado.", audit_required=True
    ),
    "SUBSCRIPTION_STATUS_CHANGED": MessageDefinition(
        "SUBSCRIPTION_STATUS_CHANGED", 200, "Status da assinatura alterado.", audit_required=True
    ),
    "SUBSCRIPTION_NOT_FOUND": MessageDefinition(
        "SUBSCRIPTION_NOT_FOUND", 404, "Assinatura não encontrada.", "warning"
    ),
    "SUBSCRIPTION_ALREADY_EXISTS": MessageDefinition(
        "SUBSCRIPTION_ALREADY_EXISTS", 409, "Assinatura já cadastrada para esta empresa.", "warning"
    ),
    "ENTITLEMENT_LIST_RETRIEVED": MessageDefinition(
        "ENTITLEMENT_LIST_RETRIEVED", 200, "Entitlements consultados com sucesso."
    ),
    "ENTITLEMENT_CHECKED": MessageDefinition(
        "ENTITLEMENT_CHECKED", 200, "Entitlement verificado com sucesso."
    ),
    "FEATURE_FLAG_SAVED": MessageDefinition(
        "FEATURE_FLAG_SAVED", 200, "Feature flag salva com sucesso.", audit_required=True
    ),
    "FEATURE_FLAG_LIST_RETRIEVED": MessageDefinition(
        "FEATURE_FLAG_LIST_RETRIEVED", 200, "Feature flags consultadas com sucesso."
    ),
    "FEATURE_FLAG_NOT_FOUND": MessageDefinition(
        "FEATURE_FLAG_NOT_FOUND", 404, "Feature flag não encontrada.", "warning"
    ),
    "BILLING_EVENT_RECORDED": MessageDefinition(
        "BILLING_EVENT_RECORDED", 200, "Evento de billing registrado.", audit_required=True
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
