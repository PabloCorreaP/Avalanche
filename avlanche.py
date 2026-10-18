import random


class Nodo:
    def __init__(self, pref: int, bizantino: bool = False) -> None:
        self.pref: int = pref            # color preferido ahora: 0 o 1
        self.d: list[int] = [0, 0]       # confianza acumulada de cada color
        self.last: int | None = None     # último color con mayoría clara
        self.cnt: int = 0                # rondas seguidas con mayoría para last
        self.decidido: bool = False      # True cuando cnt llega a beta
        self.bizantino: bool = bizantino

    def __str__(self) -> str:
        return f"{self.pref}, {self.d}, {self.last}, {self.cnt}, {self.decidido}"


def consultar(prefs: list[int], yo: int, k: int) -> list[int]:
    candidatos: list[int] = [i for i in range(len(prefs)) if i != yo]
    muestra: list[int] = random.sample(candidatos, k)
    votos: list[int] = [0, 0]
    for i in muestra:
        votos[prefs[i]] += 1
    return votos


def actualizar(nodo: Nodo, votos: list[int], alpha: int, beta: int) -> None:
    ganador: int = -1                         
    if votos[0] > votos[1]:
        if votos[0] >= alpha:                
            ganador = 0
    elif votos[1] > votos[0]:
        if votos[1] >= alpha:                 
            ganador = 1

    if ganador == -1:
        nodo.cnt=0
    else:
        nodo.d[ganador] += 1
        if nodo.d[ganador] > nodo.d[nodo.pref]:   
            nodo.pref = ganador                   
        if ganador == nodo.last:
            nodo.cnt+=1
        else:
            nodo.last=ganador
            nodo.cnt=1
        if nodo.cnt >= beta:
            nodo.decidido=True


def color_minoritario(honestos: list[Nodo]) -> int:
    a_favor_de_1: int = sum(x.pref for x in honestos)
    if a_favor_de_1 >= len(honestos) / 2:
        return 0
    return 1

def simular(n: int = 100, k: int = 20, alpha: int = 15, beta: int = 20,
            pct_bizantinos: float = 0, max_rondas: int = 1000
            ) -> tuple[str, int, int | None]:
    num_biz: int = round(n * pct_bizantinos / 100)
    nodos: list[Nodo] = [Nodo(random.choice([0, 1]), bizantino=(i < num_biz))
                         for i in range(n)]
    random.shuffle(nodos)                     # bizantinos repartidos al azar
    honestos: list[Nodo] = [x for x in nodos if not x.bizantino]
 
    for ronda in range(1, max_rondas + 1):
        # Los honestos responden con su preferencia;
        #    los bizantinos, con el color que va perdiendo entre los honestos.
        minoria: int = color_minoritario(honestos)
        prefs: list[int] = [minoria if x.bizantino else x.pref for x in nodos]
 
        #honesto no decidido consulta y actualiza
        for i, nodo in enumerate(nodos):
            if nodo.bizantino or nodo.decidido:
                continue
            votos: list[int] = consultar(prefs, i, k)
            actualizar(nodo, votos, alpha, beta)
 
        # honestos que han decidido colores distintos
        decididos: set[int] = {x.pref for x in honestos if x.decidido}
        if len(decididos) > 1:
            return "seguridad rota", ronda, None
 
        #Han decidido todos los honestos?
        if all(x.decidido for x in honestos):
            return "consenso", ronda, honestos[0].pref
 
    return "sin decision", max_rondas, None
 
 
if __name__ == "__main__":
    print("Normal (k=20, alpha=15, beta=20, sin bizantinos)")
    for _ in range(5):
        print("  ", simular())

    print("Ataque a la vivacidad (15 % bizantinos)")
    for _ in range(5):
        print("  ", simular(pct_bizantinos=15))

    print("Parámetros débiles (alpha=11, beta=2)")
    for _ in range(5):
        print("  ", simular(alpha=11, beta=2))
 
