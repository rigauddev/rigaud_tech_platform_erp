# Knowledge Architecture

Arquitetura oficial de conhecimento do Rigaud Tech Platform ERP.

## Camadas

```text
Produto
  ↓
Arquitetura
  ↓
Documentacao Tecnica
  ↓
Academy
  ↓
Help Center
  ↓
Tutoriais
  ↓
FAQ
  ↓
Materiais Comerciais
  ↓
AI/MCP Knowledge
```

## Fluxo Por Funcionalidade

Cada nova funcionalidade deve gerar, quando aplicavel:

```text
Funcionalidade
    ↓
Implementação
    ↓
Testes
    ↓
Documentação técnica
    ↓
Academy
    ↓
Help Center
    ↓
Tutorial
    ↓
FAQ
    ↓
Material comercial
```

## Fontes De Verdade

- Task Registry: rastreabilidade de entrega.
- ADRs: decisoes arquiteturais.
- ERP Decisions: decisoes permanentes de produto e dominio.
- ERP Glossary: linguagem oficial.
- Academy: aprendizagem reutilizavel.
- Help Center: uso do produto.
- README local: orientacao por modulo.

## Governanca

- Documentacao nasce junto com a funcionalidade.
- Conteudo para usuario final nao deve expor detalhes internos desnecessarios.
- Documentacao tecnica nao deve conter secrets.
- Ajuda contextual deve apontar para conteudo versionado.
- Conteudo usado por AI/MCP deve respeitar tenant, filial, role, permissoes e auditoria.

## Referencias Consultadas

- MkDocs Configuration: https://www.mkdocs.org/user-guide/configuration/
- Flutter Platform Integration: https://docs.flutter.dev/platform-integration
- Flutter Web Support: https://docs.flutter.dev/platform-integration/web
- Docker Docs: https://docs.docker.com/
- Docker Compose Production: https://docs.docker.com/compose/how-tos/production/

## Decisoes Derivadas

- A navegacao MkDocs deve usar caminhos relativos ao `docs_dir` do blueprint.
- Documentacao de plataforma deve considerar Web, Android, iOS, Windows, macOS e Linux.
- Documentacao de deployment deve separar desenvolvimento, producao, Cloud, On-Premise e Hybrid.
