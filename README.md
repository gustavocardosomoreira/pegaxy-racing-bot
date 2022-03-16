# Sobre:

Esse bot foi desenvolvido em Python e serve somente para automatizar as corridas com os pegaxies.

Ele correrá com todos os seus cavalos disponíveis para corrida, escolhendo os cavalos com mais energia primeiro.
Ele possui suporte para gerenciar múltiplas contas.

## Importante:

#### Não me responsabilizo por penalidades que o uso do bot possa trazer, use por sua conta e risco.

# Utilização:

### Baixe e instale o Python pelo [site](https://www.python.org/downloads/).

Adicione o python ao PATH do windows. O próprio instalador fornece essa opção para adicionar.

### Realize o download do codigo compactado e extraia os arquivos.

### Vá até o caminho do bot via cmd. Ex.:

```
cd c:/pegaxy-runner-bot
```

### Instale as dependências:

```
pip install -r requirements.txt
```

### Inicie o bot via o comando:

```
python main.py
```

Para todas as contas que você deseja que o bot corra com os cavalos, faça o seguinte:
- Entre no jogo e confirme que a Metamask está conectada dentro do jogo (deve aparecer o botão "My Assets" ao invés de "Connect")
- Deixe em alguma página do jogo (pode ser Rent, My Assets, Racing, não importa)
- Maximize a janela do navegador e deixe o zoom em 100%

Após rodar o comando acima, ele irá começar a interagir com as páginas.


### Importante: 
Você precisa informar ao bot qual navegador você está usando para jogar Pegaxy, para isso você deve abrir o arquivo 
`config.yaml` e editar a chave`browser`, por padrão vem configurado para o navegador Chromium.


## Como funciona / ajustes:

O bot tira screenshots da tela para localizar os botões e obter informações, baseado no estado atual do jogo o bot 
toma alguma decisão com o objetivo de correr com os cavalos. 

Por isso tem que deixar o zoom em 100% e a tela maximizada. Pelo mesmo motivo você não pode fazer mais nada na tela 
enquanto o bot está rodando.

Tudo que o bot fizer ficará logado no arquivo `logger.log`, na pasta logs.

**A lógica do bot é a seguinte:**

Ele vai tentar acessar a página de corrida dos cavalos e iniciar uma corrida com o cavalo com mais energia (ele mesmo
clica em Confirmar na Metamask), quando ele tiver certeza que a corrida começou, ele irá mudar de janela para fazer o mesmo na próxima conta, até a última. 

Terminando a última conta ele volta de novo para a primeira: se a corrida já tiver terminado, inicia outra; se ainda
estiver correndo, pula para próxima conta.

Se nenhum cavalo tiver energia para correr, define um timer de 1 hora para correr  naquela conta. Se não tiver nenhum
cavalo disponível, define um timer de 1 hora também. 

**Ajustes**

Você pode fornecer o seu próprio print dos botões para a pasta `assets/targets`, se estiver tendo problemas com o 
reconhecimento de imagens. Isso melhora a fidelidade de cores e resolução e faz com que o bot consiga localizar os 
elementos com mais assertividade. Mas **não é recomendado** fazer isso a não ser que esteja tendo problemas.

O bot foi testado na resolução 1920x1080 e os botões foram tirados desta resolução, se usá-lo em resoluções menores 
talvez ele não ele não reconheça os botões por estarem diferentes. Neste caso, pode-se tentar tirar print dos botões 
como indicado acima, mas antes confirme que a tela inteira do Pegaxy é visível com seu navegador maximizado (pois o bot
precisa ser capaz de ver a tela inteira)

Os parâmetros de funcionamento do bot podem ser configurados no arquivo config.yaml, há explicações sobre o que
cada parâmetro faz lá.
