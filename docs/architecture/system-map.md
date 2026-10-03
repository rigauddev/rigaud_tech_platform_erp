# System Map

Mapa funcional oficial da Rigaud Tech Platform ERP.

```mermaid
flowchart TD
    ERP[Rigaud Tech Platform ERP]
    ERP --> Commercial[Commercial]
    ERP --> Inventory[Inventory]
    ERP --> Restaurant[Restaurant]
    ERP --> Production[Production]
    ERP --> Financial[Financial]
    ERP --> HR[Human Resources]
    ERP --> Reports[Reports]
    ERP --> AIMCP[AI/MCP]

    Restaurant --> Inventory
    Restaurant --> Production
    Restaurant --> Financial
    Commercial --> Inventory
    Commercial --> Financial
    Production --> Inventory
    Production --> Financial
    HR --> Users[Users]
    HR --> Company[Company]
    HR --> Branch[Branch]
    AIMCP --> Events[Domain Events]
```

## Decisoes

- Production Engine e independente do Restaurant.
- Restaurant utiliza Production e Inventory.
- Financial integra Sales, Inventory, Restaurant e Production.
- HR e independente, mas integrado a Users, Company e Branch.
- AI/MCP consome eventos e ferramentas de dominio, sem alterar dados transacionais sem workflow explicito, auditoria e permissao.

## Arquitetura Viva

Este mapa deve ser atualizado quando uma task alterar arquitetura funcional, limites de modulo ou relacoes entre engines.
