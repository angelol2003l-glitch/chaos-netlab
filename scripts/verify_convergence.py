#!/usr/bin/env python3
import subprocess
import sys
import json
import re

def run_vtysh(container, cmd):
    full_cmd = ["docker", "exec", container, "vtysh", "-c", cmd]
    res = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.stdout

def check_ospf():
    print("[AUDIT] Verificando adyacencias OSPF en Leaf01...")
    out = run_vtysh("clab-chaos-netlab-leaf01", "show ip ospf neighbor")
    full_count = out.count("Full")
    if full_count >= 2:
        print(f"  [OK] OSPF adyacencias Full detectadas: {full_count}")
        return True
    else:
        print(f"  [FAIL] Se esperaban 2 adyacencias Full, detectadas: {full_count}")
        return False

def check_bgp():
    print("[AUDIT] Verificando sesiones BGP en Leaf01...")
    out = run_vtysh("clab-chaos-netlab-leaf01", "show ip bgp summary")
    # Buscamos que para los vecinos 10.1.1.0 y 10.1.1.2 State/PfxRcd sea un número > 0
    lines = [line for line in out.splitlines() if "10.1.1.0" in line or "10.1.1.2" in line]
    established = 0
    for l in lines:
        tokens = l.split()
        if len(tokens) >= 10 and tokens[9].isdigit() and int(tokens[9]) > 0:
            established += 1
            
    if established >= 2:
        print(f"  [OK] Sesiones BGP Established con prefijos: {established}")
        return True
    else:
        print(f"  [FAIL] Sesiones BGP Established insuficientes: {established}/2")
        return False

def check_bfd():
    print("[AUDIT] Verificando sesiones BFD en Leaf01...")
    out = run_vtysh("clab-chaos-netlab-leaf01", "show bfd peers")
    up_count = out.lower().count("status: up")
    if up_count >= 2:
        print(f"  [OK] Sesiones BFD Up detectadas: {up_count}")
        return True
    else:
        print(f"  [FAIL] Sesiones BFD Up insuficientes: {up_count}/2")
        return False

def check_ecmp():
    print("[AUDIT] Verificando multipath ECMP para red 192.168.20.0/24...")
    out = run_vtysh("clab-chaos-netlab-leaf01", "show ip route bgp")
    # Debe haber 2 líneas 'via' asociadas a la ruta
    lines = out.splitlines()
    has_target = any("192.168.20.0/24" in l for l in lines)
    via_count = out.count("via 10.1.1.")
    if has_target and via_count >= 2:
        print(f"  [OK] ECMP validado: 2 caminos instalados en FIB")
        return True
    else:
        print(f"  [FAIL] No se encontraron 2 caminos ECMP hacia el destino")
        return False

def main():
    print("="*50)
    print("       AUDITORÍA DE CONVERGENCIA DE RED")
    print("="*50)
    
    results = [
        ("OSPF Underlay", check_ospf()),
        ("BGP Overlay", check_bgp()),
        ("BFD Sessions", check_bfd()),
        ("ECMP Dual-Path", check_ecmp())
    ]
    
    print("\n" + "="*50)
    print("             RESUMEN DE AUDITORÍA")
    print("="*50)
    all_ok = True
    for name, status in results:
        label = "PASSED" if status else "FAILED"
        print(f"  {name.ljust(20)} : [{label}]")
        if not status:
            all_ok = False
            
    print("="*50)
    if all_ok:
        print("\n[SUCCESS] La red está 100% convergida y saludable.")
        sys.exit(0)
    else:
        print("\n[ERROR] Hay componentes de red no convergidos.")
        sys.exit(1)

if __name__ == "__main__":
    main()
