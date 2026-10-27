# Auditoría de calidad TP3

Fecha de verificación: 2026-10-26. Rama publicada: `tp3-calidad`.

## Hook y pruebas

El hook secuencial ejecutó Black 26.10.1, Ruff 0.16.10 y unittest: 13 pruebas pasaron. `coverage` midió 207 sentencias y 52 ramas; ambas con 100 %. El hook se detuvo con código 1 ante un archivo temporal con formato inválido, antes de iniciar Ruff y las pruebas. Ver `pre-commit.log`, `pre-commit-format-failure.log` y `coverage.json`.

## Análisis estático y dependencias

Radon analizó 47 bloques: complejidad promedio 2,68 (A) y máxima 10 (B), en `ProductoCombo.__init__`. Pylint no encontró duplicación y calificó 10/10. Black y Ruff no encontraron problemas. `pip-audit` encontró seis vulnerabilidades en versiones anteriores de Black, certifi y filelock; se actualizaron los pins a Black 26.10.1, certifi 2026.10.19 y filelock 4.2.1. El escaneo final no encontró vulnerabilidades conocidas. Ver `complexity.log`, `duplication.log`, `dependency-audit.log` y `outdated.log`.

## Trazabilidad

- Issue #1 (abierto): https://github.com/GastonJacinto/tp3-calidad/issues/1
- Pull Request #2 (abierta; `Fixes #1`): https://github.com/GastonJacinto/tp3-calidad/pull/2

La PR sigue sin mergear. Falta aprobación de una persona revisora según la DoD heredada de TP1. La integración no se certifica hasta completar esa revisión. SonarQube no se ejecutó; no es un requisito explícito del TP3.
