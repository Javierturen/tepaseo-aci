from statistics import mean
from time import perf_counter

from app import create_app


app = create_app()

RUTAS = [
    "/",
    "/servicios",
    "/cobertura",
    "/solicitar-paseo",
    "/trabaja-con-nosotros",
    "/admin/login",
]

REPETICIONES = 10
LIMITE_MS = 2000


def medir_rendimiento():
    print("=" * 70)
    print("TEPASEO.CL - MEDICION DE RENDIMIENTO LOCAL")
    print("=" * 70)
    print(f"Repeticiones por ruta: {REPETICIONES}")
    print(f"Tiempo objetivo: {LIMITE_MS} ms")
    print()

    with app.test_client() as client:
        for ruta in RUTAS:
            tiempos = []

            client.get(ruta)

            for _ in range(REPETICIONES):
                inicio = perf_counter()

                response = client.get(ruta)

                duracion = (perf_counter() - inicio) * 1000

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Error HTTP {response.status_code}: {ruta}"
                    )

                tiempos.append(duracion)

            promedio = mean(tiempos)
            maximo = max(tiempos)

            estado = (
                "CUMPLE"
                if maximo < LIMITE_MS
                else "NO CUMPLE"
            )

            print(
                f"{ruta:<25} "
                f"Promedio: {promedio:8.2f} ms | "
                f"Maximo: {maximo:8.2f} ms | "
                f"{estado}"
            )

    print()
    print("=" * 70)
    print("Medicion finalizada.")
    print("=" * 70)


if __name__ == "__main__":
    medir_rendimiento()
