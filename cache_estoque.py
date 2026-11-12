import argparse
from collections import OrderedDict

SEQUENCIA_PADRAO = ["A", "B", "C", "A", "D", "A", "B", "E"]


def simular(consultas, capacidade, politica):
    cache = OrderedDict()
    acertos = 0
    print(f"\n{politica} | ordem da próxima vítima até a última posição")
    print("Passo | Consulta | Resultado | Removido | Cache após consulta")
    for passo, lote in enumerate(consultas, start=1):
        removido = "-"
        if lote in cache:
            acertos += 1
            resultado = "acerto"
            if politica == "LRU":
                cache.move_to_end(lote)
        else:
            resultado = "falta"
            if len(cache) == capacidade:
                removido, _ = cache.popitem(last=False)
            cache[lote] = None
        print(f"{passo:5} | {lote:8} | {resultado:9} | {removido:8} | {', '.join(cache)}")
    faltas = len(consultas) - acertos
    print(f"{politica}: {acertos} acertos | {faltas} faltas | {acertos / len(consultas):.1%} de acerto")


def main():
    parser = argparse.ArgumentParser(description='Compara FIFO e LRU para uma sequência de consultas ao estoque.')
    parser.add_argument("--capacidade", type=int, default=3)
    parser.add_argument("lotes", nargs="*", help="identificadores na ordem das consultas")
    args = parser.parse_args()
    if args.capacidade < 1:
        parser.error("--capacidade deve ser maior ou igual a 1")
    consultas = args.lotes or SEQUENCIA_PADRAO
    for politica in ("FIFO", "LRU"):
        simular(consultas, args.capacidade, politica)


if __name__ == "__main__":
    main()
