## Requisitos

Python 3.12 o superior

## Cómo ejecutar

Abrí una terminal en esta carpeta y ejecutá:

```powershell
python main.py
```

La demo imprime cinco productos (incluidos dos combos), sus precios, clasificación, disponibilidad, productos destacados y una exportación que combina objetos del catálogo con una ficha externa. También muestra el cambio de disponibilidad y la falla temprana de la clase abstracta y de una subclase incompleta.
## Controles de calidad (TP3)

Crear y activar un entorno virtual en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Configurar y ejecutar el hook:

```powershell
git config core.hooksPath .githooks
git hook run pre-commit
```

El hook corre Black, Ruff y unittest con cobertura de ramas, en ese orden. Si un control falla, el hook se detiene y Git no crea el commit. Las evidencias reproducibles están en `evidence/`.

Auditoría estática:

```powershell
python -m radon cc -s -a catalogo.py main.py libreria_externa.py
python -m pylint --disable=all --enable=duplicate-code --min-similarity-lines=4 catalogo.py main.py libreria_externa.py
python -m pip_audit -r requirements-dev.txt
python -m pip list --outdated
```
