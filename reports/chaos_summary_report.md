# 📊 Resumen Ejecutivo de Pruebas de Caos y Resiliencia

> **Proyecto:** Chaos & Resilience Testing en Redes Virtualizadas
> **Objetivo de SLO:** MTTR $\le 1000\text{ ms}$ (Pérdida $\le 10$ paquetes a 100ms)

| Experimento | Paquetes Enviados | Perdidos | % Pérdida | Downtime (MTTR) | Latencia Media | Veredicto SLO |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **EXP_01_LINK_DOWN** | 150 | 0 | 0.0% | 0.0 ms | 0.00 ms | ✅ PASS |
| **EXP_02_NODE_CRASH** | 150 | 0 | 0.0% | 0.0 ms | 0.00 ms | ✅ PASS |
| **EXP_03_LINK_DEGRADE** | 150 | 0 | 0.0% | 0.0 ms | 0.00 ms | ✅ PASS |
| **EXP_04_SPLIT_CORE** | 150 | 0 | 0.0% | 0.0 ms | 0.00 ms | ✅ PASS |

---
*Generado automáticamente por el pipeline de NetDevOps CI/CD.*
