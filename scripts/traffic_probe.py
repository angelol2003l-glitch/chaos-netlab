#!/usr/bin/env python3
import subprocess
import time
import sys
import argparse
import json
import re

def run_probe(target_ip, count, interval, output_file):
    print(f"[PROBE] Iniciando sonda de telemetría sintética hacia {target_ip}...")
    print(f"[PROBE] Configuración: {count} paquetes a intervalos de {interval}s")
    
    cmd = [
        "docker", "exec", "clab-chaos-netlab-client-a",
        "ping", "-c", str(count), "-i", str(interval), target_ip
    ]
    
    start_time = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = proc.communicate()
    end_time = time.time()
    
    lines = stdout.splitlines()
    transmitted = 0
    received = 0
    packet_loss_pct = 100.0
    
    # Expresión regular para capturar la línea resumen de ping
    # Ejemplo: 50 packets transmitted, 48 packets received, 4% packet loss
    summary_regex = re.compile(r"(\d+)\s+packets transmitted,\s+(\d+)\s+(?:packets\s+)?received.*?(\d+(?:\.\d+)?)%\s+packet loss")
    rtt_regex = re.compile(r"rtt min/avg/max/mdev = ([\d\.]+)/([\d\.]+)/([\d\.]+)/([\d\.]+)\s+ms")
    
    rtt_stats = {"min": 0.0, "avg": 0.0, "max": 0.0}
    
    for line in lines:
        match_summary = summary_regex.search(line)
        if match_summary:
            transmitted = int(match_summary.group(1))
            received = int(match_summary.group(2))
            packet_loss_pct = float(match_summary.group(3))
            
        match_rtt = rtt_regex.search(line)
        if match_rtt:
            rtt_stats["min"] = float(match_rtt.group(1))
            rtt_stats["avg"] = float(match_rtt.group(2))
            rtt_stats["max"] = float(match_rtt.group(3))

    lost_packets = transmitted - received
    downtime_ms = lost_packets * (interval * 1000.0)
    
    telemetry_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "target": target_ip,
        "packets_transmitted": transmitted,
        "packets_received": received,
        "packets_lost": lost_packets,
        "loss_percentage": packet_loss_pct,
        "calculated_downtime_ms": downtime_ms,
        "duration_seconds": round(end_time - start_time, 2),
        "rtt_ms": rtt_stats
    }
    
    print("\n" + "="*50)
    print("           REPORTE DE TELEMETRÍA SINTÉTICA")
    print("="*50)
    print(f" Destino monitoreado:   {target_ip}")
    print(f" Paquetes enviados:     {transmitted}")
    print(f" Paquetes recibidos:    {received}")
    print(f" Paquetes perdidos:     {lost_packets}")
    print(f" Porcentaje de pérdida: {packet_loss_pct}%")
    print(f" Downtime calculado:    {downtime_ms:.1f} ms")
    print(f" Latencia RTT promedio: {rtt_stats['avg']} ms")
    print("="*50)
    
    if output_file:
        out_dir = os.path.dirname(output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(telemetry_data, f, indent=2)
        print(f"[PROBE] Datos exportados exitosamente a {output_file}")
        
    return telemetry_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sonda de Telemetría Sintética")
    parser.add_argument("--target", default="192.168.20.10", help="IP destino")
    parser.add_argument("--count", type=int, default=50, help="Cantidad de paquetes")
    parser.add_argument("--interval", type=float, default=0.1, help="Intervalo en segundos (ej. 0.1)")
    parser.add_argument("--output", default="telemetry.json", help="Archivo JSON de salida")
    
    args = parser.parse_args()
    run_probe(args.target, args.count, args.interval, args.output)
