# Academy — Demo Environment & Scenario Engine

O Demo Environment é uma ferramenta técnica para reduzir atrito em desenvolvimento, QA, treinamento e demonstrações comerciais.

## Objetivo

Um ambiente demo deve permitir:

- subir a stack com `make up`;
- carregar dados com `make demo`;
- testar fluxos existentes sem cadastro manual repetitivo;
- resetar dados operacionais sem apagar a configuração-base da plataforma.
- disponibilizar uma API e dashboard de desenvolvimento para acelerar homologação.

## Princípios

O seed precisa ser idempotente.

Isso significa que rodar o comando várias vezes não pode duplicar empresas, usuários, categorias ou produtos.

O seed também precisa respeitar a arquitetura existente. Ele não deve criar tabelas futuras, contornar migrations ou implementar regras de negócio fora dos módulos.

## Escopo Atual

Na DOC-003, o seed trabalha apenas com módulos já disponíveis:

- empresas;
- filiais;
- memberships;
- usuários;
- categorias;
- produtos.

Mesas, pedidos, estoque, clientes, QR Code e vendas ficam como cenários documentados para tasks futuras.

## Regra Permanente

Tudo que for desenvolvido deve ser demonstrável.

Ao concluir uma task funcional, o módulo deve informar como seus dados demo, cenários e validações entram no Demo Environment.
