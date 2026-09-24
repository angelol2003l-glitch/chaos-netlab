#!/usr/bin/env python3
import json
import sys
import argparse

def evaluate_slo(telemetry_file, max_lost_packets, max_downtime_ms):
    import os
    if not os.path.exists(telemetry_file) and os.path.exists(os.path.join("results", telemetry_file)):
        telemetry_file = os.path.join("results", telemetry_file)
    print(f"[SLO] Cargando telemetría desde: {telemetry_file}")
    try:
        with open(telemetry_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo de telemetría: {e}")
        sys.exit(1)
        
    lost = data.get("packets_lost", 0)
    downtime = data.get("calculated_downtime_ms", 0.0)
    loss_pct = data.get("loss_percentage", 0.0)
    
    print("\n" + "="*50)
    print("         EVALUACIÓN DE CRITERIOS SLO")
    print("="*50)
    print(f" Métrica             | Observado   | Umbral Máximo Permitido")
    print(f" --------------------|-------------|------------------------")
    print(f" Paquetes perdidos   | {str(lost).ljust(11)} | <= {max_lost_packets}")
    print(f" Downtime calculado  | {f'{downtime:.1f} ms'.ljust(11)} | <= {max_downtime_ms:.1f} ms")
    print(f" % de pérdida global | {f'{loss_pct:.1f}%'.ljust(11)} | <= 5.0%")
    print("="*50)
    
    passed = True
    reasons = []
    
    if lost > max_lost_packets:
        passed = False
        reasons.append(f"Paquetes perdidos ({lost}) exceden el umbral ({max_lost_packets})")
        
    if downtime > max_downtime_ms:
        passed = False
        reasons.append(f"Downtime ({downtime:.1f} ms) excede el SLO ({max_downtime_ms:.1f} ms)")
        
    if passed:
        print("\n [PASSED] La red CUMPLE satisfactoriamente con el SLO de Resiliencia.")
        sys.exit(0)
    else:
        print("\n [FAILED] La red NO CUMPLE con el SLO requerido:")
        for r in reasons:
            print(f"   -> {r}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluador de SLO de Resiliencia")
    parser.add_argument("--file", default="results/telemetry.json", help="Archivo JSON de telemetría")
    parser.add_argument("--max-loss", type=int, default=10, help="Máximo de paquetes perdidos permitidos")
    parser.add_argument("--max-downtime", type=float, default=1000.0, help="Downtime máximo en ms")
    
    args = parser.parse_args()
    evaluate_slo(args.file, args.max_loss, args.max_downtime)
