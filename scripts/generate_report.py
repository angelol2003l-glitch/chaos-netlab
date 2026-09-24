#!/usr/bin/env python3
import json
import glob
import os
import sys

def generate_markdown_report():
    json_files = sorted(glob.glob("results/telemetry_*.json"))
    if not json_files:
        json_files = sorted(glob.glob("telemetry_*.json"))
    
    md = []
    md.append("# 📊 Resumen Ejecutivo de Pruebas de Caos y Resiliencia")
    md.append("")
    md.append("> **Proyecto:** Chaos & Resilience Testing en Redes Virtualizadas")
    md.append(r"> **Objetivo de SLO:** MTTR $\le 1000\text{ ms}$ (Pérdida $\le 10$ paquetes a 100ms)")
    md.append("")
    md.append("| Experimento | Paquetes Enviados | Perdidos | % Pérdida | Downtime (MTTR) | Latencia Media | Veredicto SLO |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    if not json_files:
        md.append("| *No se encontraron archivos de telemetría* | - | - | - | - | - | ⚠️ SIN DATOS |")
    else:
        for jf in json_files:
            try:
                with open(jf, "r") as f:
                    data = json.load(f)
                    
                exp_name = os.path.basename(jf).replace("telemetry_", "").replace(".json", "").upper()
                sent = data.get("packets_transmitted", 0)
                lost = data.get("packets_lost", 0)
                pct = data.get("loss_percentage", 0.0)
                downtime = data.get("calculated_downtime_ms", 0.0)
                rtt_avg = data.get("rtt_ms", {}).get("avg", 0.0)
                
                # Criterio SLO: <= 10 paquetes perdidos y <= 1000 ms
                passed = (lost <= 10 and downtime <= 1000.0)
                badge = "✅ PASS" if passed else "❌ FAIL"
                
                md.append(f"| **{exp_name}** | {sent} | {lost} | {pct:.1f}% | {downtime:.1f} ms | {rtt_avg:.2f} ms | {badge} |")
            except Exception as e:
                md.append(f"| Error leyendo {jf} | - | - | - | - | - | ⚠️ ERROR |")
                
    md.append("")
    md.append("---")
    md.append("*Generado automáticamente por el pipeline de NetDevOps CI/CD.*")
    
    report_text = "\n".join(md)
    print(report_text)
    
    # Si estamos en un entorno de GitHub Actions, exportar al Step Summary
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write(report_text + "\n")
        print(f"\n[REPORT] Reporte publicado en GITHUB_STEP_SUMMARY ({summary_path})")
    
    report_file = os.path.join("reports", "chaos_summary_report.md")
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, "w") as f:
        f.write(report_text + "\n")
    print(f"\n[REPORT] Reporte guardado localmente en '{report_file}'")

if __name__ == "__main__":
    generate_markdown_report()
