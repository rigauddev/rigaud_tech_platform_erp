# Help Center Architecture

DOC-009 define a arquitetura da futura Central de Ajuda do Rigaud Tech Platform ERP.

## Publicos

A documentacao precisa atender:

- desenvolvedores;
- DevOps;
- administradores do sistema;
- implantadores;
- suporte tecnico;
- parceiros;
- revendedores;
- gestores;
- usuarios finais;
- equipe comercial;
- equipe de marketing;
- futuros agentes de IA/MCP.

## Separacao Oficial

### Documentacao Tecnica

Destinada a:

- desenvolvimento;
- implantacao;
- infraestrutura;
- suporte tecnico;
- parceiros tecnicos.

Exemplos:

- arquitetura;
- APIs;
- banco de dados;
- deployment;
- troubleshooting tecnico;
- seguranca.

### Documentacao Do Usuario

Destinada a:

- funcionarios;
- gestores;
- administradores;
- operadores.

Exemplos:

- como cadastrar produto;
- como consultar saldo;
- como operar recebimento;
- como acessar ajuda de uma tela.

### Help Center

Destinado a:

- duvidas frequentes;
- passo a passo;
- primeiros passos;
- problemas comuns;
- utilizacao das funcionalidades.

## Ajuda Dentro Do ERP

Arquitetura futura:

```text
ERP
  └── ?
      ├── Ajuda
      ├── Tutorial
      ├── FAQ
      ├── Documentação
      └── Suporte
```

Cada tela podera apontar para um conteudo especifico.

Exemplo futuro:

```text
Produtos
  ?
  ↓
Como cadastrar produto
```

## Limite Atual

DOC-009 nao implementa Help Center no frontend, busca, CMS, suporte online ou agentes de IA.

## Guias disponíveis

- [QR Codes das mesas](restaurant/table-qr-codes.md)
