#!/usr/bin/env python3

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fase 2: Crear/actualizar evangelios del día (stub)."
    )
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: hoy)")
    parser.add_argument("--days-ahead", type=int, default=3, help="Ventana futura")
    parser.add_argument("--dry-run", action="store_true", help="No escribe en el panel")
    args = parser.parse_args()

    print(
        "FASE 2 (Evangelio) aun no implementada. Ver especificacion en docs/fases/FASE_2_EVANGELIO.md."
    )
    print(f"Parametros: start_date={args.start_date} days_ahead={args.days_ahead} dry_run={args.dry_run}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
