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
