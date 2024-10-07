# Sistema de Gerenciamento de Estacionamento - UEL
Repositório destinado ao desenvolvimento de um sistema distribuído para gerenciar o controle de vagas em um estacionamento.

## Descrição do Projeto
Este projeto tem como objetivo gerenciar um estacionamento com múltiplas estações de entrada e saída, onde cada estação controla parte das vagas. O sistema é distribuído, com comunicação entre as estações e uma Central de Controle. O objetivo principal é garantir a disponibilidade e alocação eficiente das vagas, além de lidar com falhas e redistribuição de vagas em caso de falhas nas estações.

O sistema foi desenvolvido utilizando sockets para comunicação e simula a dinâmica de um estacionamento em tempo real. A Central de Controle pode enviar comandos para ativar ou desativar estações, e as estações comunicam informações sobre as vagas que controlam.

## Funcionalidades Principais
- Ativação e Desativação de Estações: O sistema permite ativar ou desativar estações de controle de entrada/saída, simulando falhas ou manutenção.
- Redistribuição de Vagas: Quando uma estação falha, suas vagas são redistribuídas para outras estações ativas.
- Gerenciamento de Veículos: O sistema registra a entrada e saída de veículos nas vagas controladas por cada estação.
- Comunicação entre Estações e Central: Todas as estações reportam a situação de suas vagas para a Central de Controle.
- Tolerância a Falhas: Em caso de falha de uma estação, as demais continuam funcionando e podem herdar as vagas da estação inativa.

## Tecnologias Utilizadas
- Python: Linguagem principal utilizada no projeto.
- Sockets: Para a comunicação entre a Central de Controle e as estações.
- Arquitetura distribuída: Cada estação tem sua própria instância, e a Central gerencia todas elas.

## Como Rodar o Projeto
### Pré-requisitos
- Certifique-se de ter o Python instalado em sua máquina. Você pode verificar isso rodando o comando:

  ```bash
  python --version
  ```

  - Se não estiver instalado, você pode fazer o download no [Site oficial do Python](https://www.python.org/downloads/)

### Passos para Executar
  1. Clone o repositório:
     
```bash
    git clone https://github.com/LuccaGiovane/UEL-Estacionamento.git
  ```
  2. Navegue até o diretório do projeto:

```bash
    cd UEL-Estacionamento
  ```

  3. Iniciar o projeto:
     
```bash
    make run
  ```

## Comandos Disponíveis
- AE n: Ativar a estação de número n.
- DE n: Desativar a estação de número n.
- RV n: Request de vaga de um veículo para a estação de número n.
- LV n: Request para liberar uma vaga na estação de número n.
- V n: Verificar o número de vagas totais, livres e ocupadas da estação de número n.

## Contribuições
Sinta-se à vontade para abrir issues ou pull requests se desejar contribuir com melhorias ou reportar problemas.
