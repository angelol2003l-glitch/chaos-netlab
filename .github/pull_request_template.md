## Description
Briefly describe the purpose of this PR and what network components or chaos experiments are affected.

## Type of Change
- [ ] 🧪 New Chaos Experiment
- [ ] 🌐 Topology or Routing Config Update (OSPF / BGP / BFD)
- [ ] 📊 Telemetry, Metrics, or SLO Improvement
- [ ] 🚀 CI/CD Pipeline Enhancement
- [ ] 📝 Documentation Update

## Resilience Verification
- [ ] Pre-flight convergence check passed (`scripts/verify_convergence.py`)
- [ ] Chaos suite executed without unintended drops (`scripts/chaos_runner.py`)
- [ ] SLO criteria verified (MTTR <= 1000ms, packet loss <= 10 packets)
- [ ] Executive report generated and reviewed (`reports/chaos_summary_report.md`)
