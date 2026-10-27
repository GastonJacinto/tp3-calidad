import io
import runpy
import unittest
from contextlib import redirect_stdout

import main


class MainTests(unittest.TestCase):
    def test_demo_imprime_catalogo_y_evidencias_de_diseno(self):
        salida = io.StringIO()
        with redirect_stdout(salida):
            main.main()

        texto = salida.getvalue()
        self.assertIn("CATÁLOGO FOOD STORE", texto)
        self.assertIn("PRODUCTO|Agua mineral", texto)
        self.assertIn("POS|PV-01|Caja principal", texto)
        self.assertIn("Falla temprana ABC:", texto)
        self.assertIn("Falla temprana de subclase:", texto)

    def test_modulo_ejecutable_tambien_corre_la_demo(self):
        salida = io.StringIO()
        with redirect_stdout(salida):
            runpy.run_module("main", run_name="__main__")
        self.assertIn("CATÁLOGO FOOD STORE", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
