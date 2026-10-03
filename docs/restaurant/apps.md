# Experiências Restaurant no Flutter

O projeto mantém uma única base Flutter e um único backend. As experiências abaixo são superfícies por papel, feature flag, tamanho de tela e contexto operacional, e não projetos independentes.

| Experiência | Público | Próxima task de origem |
| --- | --- | --- |
| Gestão | proprietário, gerente e administrativo | RESTAURANT-001 em diante |
| Garçom | atendimento móvel | RESTAURANT-003 e RESTAURANT-009 |
| Cozinha/Bar (KDS) | estação de preparo | RESTAURANT-010 |
| PDV/Caixa | operador de caixa | RESTAURANT-013 planejada |
| Cliente/Menu Online | cliente por QR ou canal público | RESTAURANT-005 a RESTAURANT-008 |

Cada experiência reutilizará autenticação, contexto ativo, envelope da API, observabilidade, RBAC e componentes do Design System já existentes. A adaptação Web, Android, iOS, Windows, Linux e macOS é obrigatória para cada tela entregue.

Aplicativos nativos separados só poderão ser avaliados por ADR quando houver requisito técnico ou comercial que não possa ser atendido pela base única.
