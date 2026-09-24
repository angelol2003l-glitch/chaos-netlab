# Contributing to Chaos-Netlab

Thank you for your interest in contributing to **Chaos-Netlab**! We welcome contributions that improve network resilience testing, add new chaos experiments, or enhance NetDevOps automation.

## How to Contribute

### 1. Adding New Chaos Experiments
When proposing a new chaos experiment:
- Define the hypothesis and steady-state verification.
- Implement the injection and recovery logic inside `scripts/chaos_runner.py`.
- Ensure non-disruptive teardown and self-healing.
- Verify SLO compliance against high-frequency telemetry.

### 2. Modifying Routing Topologies
- Update `topology.clab.yml` with any new interfaces or nodes.
- Maintain consistent FRR configurations in `configs/<node>/frr.conf`.
- Ensure OSPF, BGP, and BFD timers are synchronized across peers.

### 3. Submitting Changes
1. Fork the repository and create your branch (`git checkout -b feature/new-experiment`).
2. Test your changes locally using `sudo python3 scripts/chaos_runner.py --exp all`.
3. Ensure CI pipeline checks pass (`verify_convergence.py` and SLO validation).
4. Commit your changes with clear semantic commit messages (`feat: ...`, `fix: ...`, `docs: ...`).
5. Open a Pull Request describing your hypothesis and results.
