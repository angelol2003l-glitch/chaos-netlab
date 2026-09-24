import os
#!/usr/bin/env python3
import subprocess
import time
import sys
import argparse
import json

def run_cmd(cmd_list, capture=True):
    res = subprocess.run(cmd_list, stdout=subprocess.PIPE if capture else None,
                         stderr=subprocess.PIPE if capture else None, text=True)
    return res

def run_experiment_lifecycle(name, description, inject_fn, recover_fn, duration=15, fault_delay=3):
    print("\n" + "="*60)
    print(f" EXPERIMENTO DE CAOS: {name}")
    print(f" Descripción: {description}")
    print("="*60)
    
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"telemetry_{name.lower().replace('-', '_')}.json")
    total_packets = duration * 10  # 10 paquetes por segundo (intervalo 0.1s)
    
    # 1. Iniciar sonda de tráfico en segundo plano
    print(f"[1/5] Iniciando telemetría sintética ({total_packets} paquetes a 100ms)...")
    probe_cmd = [
        "python3", "scripts/traffic_probe.py",
        "--count", str(total_packets),
        "--interval", "0.1",
        "--output", output_file
    ]
    probe_proc = subprocess.Popen(probe_cmd)
    
    # 2. Esperar período de estado estacionario (steady-state)
    time.sleep(fault_delay)
    
    # 3. Inyectar falla
    print(f"[2/5] INYECTANDO FALLA...")
    inject_fn()
    
    # 4. Esperar tiempo de observación con falla activa
    observe_time = duration - fault_delay - 3
    if observe_time > 0:
        time.sleep(observe_time)
        
    # 5. Restaurar entorno
    print(f"[3/5] RESTAURANDO ENTORNO...")
    recover_fn()
    
    # 6. Esperar a que la sonda termine
    print(f"[4/5] Esperando finalización de telemetría...")
    probe_proc.wait()
    
    # 7. Evaluar SLO
    print(f"[5/5] Evaluando cumplimiento de SLO de Resiliencia...")
    slo_cmd = [
        "python3", "scripts/evaluate_slo.py",
        "--file", output_file,
        "--max-loss", "10",       # Máximo 10 paquetes perdidos (1.0s)
        "--max-downtime", "1000.0" # Máximo 1000 ms
    ]
    slo_res = subprocess.run(slo_cmd)
    
    # Pequeña pausa para reconvergencia limpia antes del siguiente test
    time.sleep(3)
    return slo_res.returncode == 0

# --- DEFINICIÓN DE EXPERIMENTOS ---

def exp01_link_down():
    # EXP-01: Caída de enlace Leaf01 -> Spine01 (eth1)
    run_cmd(["docker", "exec", "clab-chaos-netlab-leaf01", "ip", "link", "set", "eth1", "down"])

def exp01_link_up():
    run_cmd(["docker", "exec", "clab-chaos-netlab-leaf01", "ip", "link", "set", "eth1", "up"])

def exp02_node_kill():
    # EXP-02: Caída/congelamiento súbito de Spine01 (preserva veth en Containerlab)
    run_cmd(["docker", "pause", "clab-chaos-netlab-spine01"])

def exp02_node_recover():
    run_cmd(["docker", "unpause", "clab-chaos-netlab-spine01"])
    # Dar tiempo a que FRR re-establezca sesiones
    time.sleep(5)

def exp03_netem_degrade():
    # EXP-03: Falla gris (25% pérdida y 50ms latencia en eth1 de Leaf01)
    run_cmd(["docker", "exec", "clab-chaos-netlab-leaf01", "tc", "qdisc", "add", "dev", "eth1", "root", "netem", "loss", "25%", "delay", "50ms"])

def exp03_netem_clean():
    run_cmd(["docker", "exec", "clab-chaos-netlab-leaf01", "tc", "qdisc", "del", "dev", "eth1", "root"])

def exp04_interspine_down():
    # EXP-04: Caída del enlace Inter-Spine (eth3 en Spine01)
    run_cmd(["docker", "exec", "clab-chaos-netlab-spine01", "ip", "link", "set", "eth3", "down"])

def exp04_interspine_up():
    run_cmd(["docker", "exec", "clab-chaos-netlab-spine01", "ip", "link", "set", "eth3", "up"])

def main():
    parser = argparse.ArgumentParser(description="Motor de Inyección de Chaos Engineering")
    parser.add_argument("--exp", choices=["exp01", "exp02", "exp03", "exp04", "all"], default="all",
                        help="Experimento a ejecutar (default: all)")
    args = parser.parse_args()
    
    experiments = {
        "exp01": ("EXP-01-LINK-DOWN", "Corte de enlace primario Leaf01 <-> Spine01", exp01_link_down, exp01_link_up),
        "exp02": ("EXP-02-NODE-CRASH", "Caída catastrófica del router Core Spine-01", exp02_node_kill, exp02_node_recover),
        "exp03": ("EXP-03-LINK-DEGRADE", "Falla gris con 25% de pérdida y 50ms de retardo", exp03_netem_degrade, exp03_netem_clean),
        "exp04": ("EXP-04-SPLIT-CORE", "Corte del enlace de interconexión Spine01 <-> Spine02", exp04_interspine_down, exp04_interspine_up)
    }
    
    print("="*60)
    print("   INICIANDO SUITE DE RESILIENCIA Y CHAOS ENGINEERING")
    print("="*60)
    
    # 0. Auditoría previa: verificar que la red esté saludable antes de romperla
    print("\n[PRE-FLIGHT] Verificando salud inicial de la red...")
    check = subprocess.run(["python3", "scripts/verify_convergence.py"])
    if check.returncode != 0:
        print("\n[ABORT] La red no está en estado estacionario saludable. Abortando pruebas.")
        sys.exit(1)
        
    to_run = [args.exp] if args.exp != "all" else ["exp01", "exp02", "exp03", "exp04"]
    results = {}
    
    for key in to_run:
        tag, desc, inj, rec = experiments[key]
        success = run_experiment_lifecycle(tag, desc, inj, rec)
        results[tag] = "PASSED" if success else "FAILED"
        
    print("\n" + "="*60)
    print("             TABLERO RESUMEN DE CHAOS TESTING")
    print("="*60)
    overall_pass = True
    for tag, status in results.items():
        print(f"  {tag.ljust(25)} : [{status}]")
        if status != "PASSED":
            overall_pass = False
    print("="*60)
    
    if overall_pass:
        print("\n[SUCCESS] Todos los experimentos de resiliencia CUMPLIERON con el SLO.")
        sys.exit(0)
    else:
        print("\n[FAIL] Uno o más experimentos violaron el umbral de disponibilidad.")
        sys.exit(1)

if __name__ == "__main__":
    main()
