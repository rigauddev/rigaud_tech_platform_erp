# Cliente Windows: disponibilidade e instalacao

## Existe um instalador Windows para baixar?

Ainda nao. O projeto nao publica um instalador Windows (`.msi`, `.msix` ou
`Setup.exe`) para usuarios finais. Nao execute arquivos de instalacao obtidos
de fontes nao oficiais.

Para desenvolvimento local, o ERP pode ser acessado pelo navegador em
`http://localhost:3000` quando a stack local estiver em execucao. O cliente
Flutter desktop para Windows pode ser compilado a partir do codigo-fonte por um
desenvolvedor com as ferramentas apropriadas; esse build nao e um instalador de
producao.

Consulte o
[guia de desenvolvimento e teste desktop no Windows](../frontend/windows-desktop-installation.md)
para os pre-requisitos, comandos e limites do build local.

## Windows como servidor On-Premise

O aplicativo Windows e um cliente do ERP, nao o servidor On-Premise. A
arquitetura recomenda Linux para o servidor On-Premise. Um dispositivo Windows
cliente acessa a URL fornecida pelo administrador da instalacao e precisa ter
conectividade de rede com esse servidor.

## Suporte

Quando o instalador oficial estiver disponivel, esta pagina devera receber o
link autenticado de distribuicao, versoes suportadas, instrucoes de
atualizacao, requisitos de runtime e procedimento de desinstalacao.
