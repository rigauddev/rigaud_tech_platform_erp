class MessageResolver {
  const MessageResolver();

  String resolve(String? code, String? apiMessage) {
    if (apiMessage != null && apiMessage.isNotEmpty) {
      return apiMessage;
    }
    return switch (code) {
      'AUTH_INVALID_CREDENTIALS' => 'Credenciais inválidas.',
      'AUTH_FORBIDDEN' => 'Permissão negada.',
      'USER_NOT_FOUND' => 'Usuário não encontrado.',
      'COMPANY_NOT_FOUND' => 'Empresa não encontrada.',
      'VALIDATION_ERROR' => 'Existem dados inválidos na requisição.',
      _ => 'Não foi possível concluir a operação.',
    };
  }
}
