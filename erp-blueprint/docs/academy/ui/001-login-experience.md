# Login Experience

Uma tela de login de ERP precisa parecer segura, clara e operacional.

Na UI-001, o login deixa de ser uma tela técnica e passa a usar:

- fundo fixo com identidade visual da Rigaud Tech;
- card de autenticação centralizado;
- logo em leitura horizontal;
- campos de email e senha;
- rodapé com versão, build, API e ambiente.

O layout evita scroll externo porque a tela de login deve ocupar o viewport inteiro. Quando o teclado abre, o formulário sobe usando `viewInsets`, enquanto o background permanece estável.

Essa base visual deve orientar telas futuras de recuperação de senha, bloqueio e seleção administrativa de contexto.
