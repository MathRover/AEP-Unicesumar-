# Simulação de concorrência e substituição de páginas no Banco de Alimentos de Londrina

**UniCesumar · Engenharia de Software · 4º semestre**  
**Sistemas Operacionais · AEP 2026.2 · Segunda entrega**  
**Integrantes** 
<br>
Maria Eduarda Bueno de Azevedo RA: 25177957-2, 
<br>
Matheus Rover da Silva RA: 25032458-2,
<br>
Samuel de Oliveira Campos RA: 25235501-2
**Londrina · 2026**

## Resumo

Este trabalho simula o recebimento e a expedição concorrentes de lotes no Banco de Alimentos de Londrina. A solução usa threads, um mutex e dois semáforos para controlar o acesso a um buffer limitado. Um segundo programa representa as consultas ao estoque como referências a páginas e compara FIFO e LRU com a mesma capacidade e sequência de acessos.

**Palavras-chave** concorrência, semáforo, produtor-consumidor, FIFO, LRU.

## 1 Introdução

No galpão, diferentes postos podem receber doações e expedir lotes ao mesmo tempo. Se duas operações acessarem a mesma fila sem coordenação, podem tomar decisões a partir de um estado desatualizado. Por exemplo, duas expedições podem tentar retirar o único lote disponível. O simulador representa a área de espera do galpão por uma fila em memória e usa cada identificador de lote para verificar o caminho do recebimento até a expedição.

## 2 Simulação do galpão

Cada posto de recepção é uma thread produtora. Cada posto de expedição é uma thread consumidora. Todas são iniciadas antes de um sinal comum liberar o trabalho. A ordem de execução das threads depende do escalonamento. A retirada segue a ordem efetiva de entrada dos lotes na fila.

| Primitiva | Estado inicial | Responsabilidade |
| --- | --- | --- |
| `Lock` (mutex) | Destravado | Protege inserções, remoções e registros de movimentação |
| `BoundedSemaphore` de vagas | Capacidade do buffer | Reserva espaço antes de uma inserção |
| `Semaphore` de itens disponíveis | Zero | Reserva um item antes de uma remoção |

A recepção adquire uma vaga, insere o lote sob o mutex e sinaliza um item disponível depois de liberar o mutex. A expedição adquire um item disponível, remove o lote sob o mutex e devolve uma vaga depois de liberar o mutex. As primitivas de `threading` sincronizam threads reais, enquanto o estoque do galpão é representado em memória.

### 2.1 Condições de corrida e deadlock

A reserva por semáforo impede que dois consumidores usem a mesma permissão de retirada. O mutex garante que apenas uma thread manipule a fila por vez. O mesmo princípio vale na recepção, com uma permissão para cada vaga e inserções protegidas pelo mutex.

Uma thread que espera por vaga ou item ainda não adquiriu o mutex. Com a fila cheia, a expedição pode entrar na seção crítica, retirar um lote e liberar espaço. Com a fila vazia, a recepção pode entrar, inserir e sinalizar um item. Como cada trabalhador espera pelo seu semáforo antes de tomar o mutex e libera o mutex antes de sinalizar o outro semáforo, o protocolo evita a espera circular por esses recursos.

Depois que todas as recepções terminam, a thread principal insere um marcador de encerramento por expedição. Os marcadores passam pelo mesmo buffer e ficam atrás dos lotes reais ainda pendentes. Cada expedição termina ao consumir um marcador. Ao final, o programa confere a integridade dos lotes, a ordem das retiradas, o limite de ocupação e a fila vazia.

### 2.2 Resultados do galpão

| Vagas | Recepção | Expedição | Lotes por execução | Execuções concluídas |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 4 | 4 | 1.000 | 30 |
| 1 | 1 | 8 | 1 | 5 |
| 2 | 8 | 1 | 400 | 5 |

As 40 execuções da tabela passaram nas verificações, com limite externo de 5 segundos por execução. O segundo cenário também verifica o encerramento quando há mais expedidores que lotes.

## 3 Simulação do cache de estoque

Cada identificador representa uma página do cache simulado. A consulta gera um acerto quando a página já está carregada e uma falta quando precisa ser inserida. Quando o cache está cheio, FIFO remove a página que entrou há mais tempo. LRU remove a que está há mais tempo sem acesso, pois cada acerto atualiza a ordem de uso.

O cenário principal inicia com o cache vazio, três posições e as consultas A, B, C, A, D, A, B, E.

| Política | Consultas | Acertos | Faltas | Taxa de acerto |
| --- | ---: | ---: | ---: | ---: |
| FIFO | 8 | 1 | 7 | 12,5% |
| LRU | 8 | 2 | 6 | 25,0% |

Na quarta consulta, ambas as políticas encontram A no cache. Quando D chega, FIFO remove A, a página inserida primeiro. LRU remove B, que tem o acesso mais antigo após a atualização de A. A sexta consulta, novamente a A, explica a diferença de um acerto entre as políticas.

A vantagem depende do padrão de acesso. Com duas posições e a sequência A, B, A, C, B, FIFO obtém dois acertos e LRU obtém um. O protótipo compara faltas no cache em memória, uma abstração da substituição de páginas. Os números medem acertos e faltas da sequência simulada.

## 4 Conclusão

O galpão simulou requisições simultâneas e manteve a integridade e a ordem dos lotes mesmo com uma única vaga no buffer. A comparação do cache mostrou como o critério de remoção altera as faltas para uma mesma carga de consultas. Para avaliar a melhor política em uma implantação real, seria necessário medir a sequência de consultas do sistema em operação.

## Apêndice A — Execução e demonstração

Extraia o pacote, abra o terminal na pasta extraída e execute com Python 3. No Windows, use `py` no lugar de `python` se esse for o comando disponível.

```text
python galpao.py --detalhar
python galpao.py --capacidade 1 --recepcoes 4 --expedicoes 4 --lotes 250
python cache_estoque.py
python cache_estoque.py --capacidade 2 A B A C B
```

Na primeira execução, cada linha mostra a operação e a ocupação após a movimentação. Na segunda, confira 1.000 lotes recebidos, 1.000 expedidos, pico de 1/1 e fila vazia. No cache, acompanhe as linhas 4 a 6 para observar a diferença entre as remoções de FIFO e LRU.
