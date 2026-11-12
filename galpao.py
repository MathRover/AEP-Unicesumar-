import argparse
from collections import Counter, deque
from threading import BoundedSemaphore, Event, Lock, Semaphore, Thread


class BufferGalpao:
    def __init__(self, capacidade, detalhar=False):
        self.fila = deque()
        self.vagas = BoundedSemaphore(capacidade)
        self.disponiveis = Semaphore(0)
        self.mutex = Lock()
        self.detalhar = detalhar
        self.recebidos = []
        self.expedidos = []
        self.pico = 0

    def receber(self, lote):
        self.vagas.acquire()
        with self.mutex:
            self.fila.append(lote)
            self.pico = max(self.pico, len(self.fila))
            if lote is not None:
                self.recebidos.append(lote)
                if self.detalhar:
                    print(f"Recepção  | {lote:5} | fila = {len(self.fila)}")
        self.disponiveis.release()

    def expedir(self):
        self.disponiveis.acquire()
        with self.mutex:
            lote = self.fila.popleft()
            if lote is not None:
                self.expedidos.append(lote)
                if self.detalhar:
                    print(f"Expedição | {lote:5} | fila = {len(self.fila)}")
        self.vagas.release()
        return lote


def simular(capacidade, recepcoes, expedicoes, lotes_por_recepcao, detalhar):
    galpao = BufferGalpao(capacidade, detalhar)
    inicio = Event()
    grupos = [
        [f"R{recepcao:02d}-{lote:02d}" for lote in range(1, lotes_por_recepcao + 1)]
        for recepcao in range(1, recepcoes + 1)
    ]

    def trabalhar_recepcao(lotes):
        inicio.wait()
        for lote in lotes:
            galpao.receber(lote)

    def trabalhar_expedicao():
        inicio.wait()
        while galpao.expedir() is not None:
            pass

    produtores = [
        Thread(target=trabalhar_recepcao, args=(lotes,), name=f"Recepção-{indice}")
        for indice, lotes in enumerate(grupos, start=1)
    ]
    consumidores = [
        Thread(target=trabalhar_expedicao, name=f"Expedição-{indice}")
        for indice in range(1, expedicoes + 1)
    ]

    for trabalhador in produtores + consumidores:
        trabalhador.start()
    inicio.set()

    for trabalhador in produtores:
        trabalhador.join()
    for _ in consumidores:
        galpao.receber(None)
    for trabalhador in consumidores:
        trabalhador.join()

    esperados = Counter(lote for grupo in grupos for lote in grupo)
    if Counter(galpao.recebidos) != esperados or Counter(galpao.expedidos) != esperados:
        raise RuntimeError("Divergência entre os lotes esperados, recebidos e expedidos.")
    if galpao.recebidos != galpao.expedidos:
        raise RuntimeError("A expedição violou a ordem FIFO do buffer.")
    if galpao.fila or not 0 < galpao.pico <= capacidade:
        raise RuntimeError("O estado final ou o pico de ocupação do buffer é inválido.")

    print(f"Recebidos: {len(galpao.recebidos)} | Expedidos: {len(galpao.expedidos)}")
    print(f"Pico de ocupação do buffer: {galpao.pico}/{capacidade} posições")
    print("Verificação OK: lotes completos e únicos, ordem FIFO e buffer vazio.")


def positivo(valor):
    numero = int(valor)
    if numero < 1:
        raise argparse.ArgumentTypeError("informe um inteiro maior ou igual a 1")
    return numero


def main():
    parser = argparse.ArgumentParser(description='Simulação concorrente de recebimento e expedição de lotes.')
    parser.add_argument("--capacidade", type=positivo, default=3)
    parser.add_argument("--recepcoes", type=positivo, default=2)
    parser.add_argument("--expedicoes", type=positivo, default=2)
    parser.add_argument("--lotes", type=positivo, default=4, help="lotes por recepção")
    parser.add_argument("--detalhar", action="store_true", help="mostra cada movimentação")
    args = parser.parse_args()
    simular(args.capacidade, args.recepcoes, args.expedicoes, args.lotes, args.detalhar)


if __name__ == "__main__":
    main()
