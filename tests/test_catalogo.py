import math
import unittest

from catalogo import (
    Categoria,
    ErrorDominio,
    Producto,
    ProductoCombo,
    ProductoDestacado,
    ProductoPorPeso,
    ProductoSimple,
    UnidadMedida,
    exportar_catalogo,
)
from libreria_externa import FichaPuntoDeVenta


class ProductoPrueba(Producto):
    def precio_final(self, cantidad: float) -> float:
        return self.precio_base * cantidad


class CatalogoTests(unittest.TestCase):
    def setUp(self):
        self.bebidas = Categoria("Bebidas")
        self.almacen = Categoria("Almacén")
        self.unidad = UnidadMedida("unidad", "u", "unidad")

    def test_unidad_medida_rechaza_campos_vacios_o_no_textuales(self):
        for valores in [
            (" ", "u", "unidad"),
            ("unidad", None, "unidad"),
            ("unidad", "u", ""),
        ]:
            with self.subTest(valores=valores), self.assertRaises(ErrorDominio):
                UnidadMedida(*valores)

    def test_categoria_valida_normaliza_nombre_y_rechaza_entradas_invalidas(self):
        categoria = Categoria("  Bebidas  ", " Para tomar ")
        self.assertEqual(categoria.nombre, "Bebidas")
        self.assertEqual(categoria.descripcion, " Para tomar ")
        for nombre in (None, " "):
            with self.subTest(nombre=nombre), self.assertRaises(ErrorDominio):
                Categoria(nombre)
        with self.assertRaises(ErrorDominio):
            Categoria("Bebidas", 1)

    def test_producto_valida_datos_base_y_expone_estado(self):
        producto = ProductoPrueba("  Agua ", 10, 2, self.bebidas, self.unidad)
        self.assertEqual(producto.nombre, "Agua")
        self.assertEqual(producto.precio_base, 10)
        self.assertIs(producto.unidad_venta, self.unidad)
        self.assertTrue(producto.disponible)
        self.assertEqual(producto.precio_publicado, "$ 10.00 / u")
        producto.deshabilitar()
        self.assertFalse(producto.disponible)
        producto.habilitar()
        self.assertTrue(producto.disponible)

        invalid_products = [
            (" ", 10, 2, self.bebidas, None, True),
            ("Agua", True, 2, self.bebidas, None, True),
            ("Agua", -1, 2, self.bebidas, None, True),
            ("Agua", math.inf, 2, self.bebidas, None, True),
            ("Agua", 10, -1, self.bebidas, None, True),
            ("Agua", 10, 2, object(), None, True),
            ("Agua", 10, 2, self.bebidas, object(), True),
            ("Agua", 10, 2, self.bebidas, None, 1),
        ]
        for args in invalid_products:
            with self.subTest(args=args), self.assertRaises(ErrorDominio):
                ProductoPrueba(*args)

    def test_producto_abstracto_no_se_instancia(self):
        with self.assertRaises(TypeError):
            Producto("Abstracto", 1, 1, self.bebidas)

    def test_producto_simple_calcula_y_valida_cantidad_entera(self):
        producto = ProductoSimple("Agua", 12, 5, self.bebidas)
        self.assertEqual(producto.precio_final(3), 36)
        for cantidad in (True, 0, -1, 1.5, math.nan, "2"):
            with self.subTest(cantidad=cantidad), self.assertRaises(ErrorDominio):
                producto.precio_final(cantidad)

    def test_producto_por_peso_calcula_y_valida_peso_positivo(self):
        producto = ProductoPorPeso("Queso", 9.99, 5, self.bebidas)
        self.assertEqual(producto.precio_final(1.25), 12.49)
        for peso in (True, "1", 0, -1, math.inf):
            with self.subTest(peso=peso), self.assertRaises(ErrorDominio):
                producto.precio_final(peso)

    def test_producto_admite_una_sola_categoria_principal(self):
        producto = ProductoSimple("Agua", 1, 1, self.bebidas)
        producto.clasificar_en(self.almacen)
        principal = Categoria("Fiambrería")
        producto.clasificar_en(principal, es_principal=True)
        self.assertIs(producto.categoria_principal(), principal)
        self.assertEqual(
            tuple(v.es_principal for v in producto.categorias()), (False, False, True)
        )
        with self.assertRaises(ErrorDominio):
            producto.clasificar_en(object())
        with self.assertRaises(ErrorDominio):
            producto.clasificar_en(self.almacen)
        with self.assertRaises(ErrorDominio):
            producto.clasificar_en(Categoria("Nueva"), es_principal=1)

    def test_exportar_catalogo_acepta_productos_y_objetos_exportables(self):
        producto = ProductoSimple("Agua", 10, 1, self.bebidas)
        ficha = FichaPuntoDeVenta("PV-01", "Caja")
        self.assertEqual(
            exportar_catalogo([producto, ficha]),
            ["PRODUCTO|Agua|$ 10.00|Bebidas", "POS|PV-01|Caja"],
        )

    def test_combo_calcula_descuento_y_copia_componentes(self):
        agua = ProductoSimple("Agua", 100, 1, self.bebidas)
        queso = ProductoPorPeso("Queso", 200, 1, self.almacen)
        componentes = [agua, queso]
        combo = ProductoCombo("Combo", componentes, 0.25, 3, self.bebidas)
        componentes.clear()
        self.assertEqual(combo.precio_base, 300)
        self.assertEqual(combo.precio_final(2), 450)
        self.assertEqual(combo.componentes(), (agua, queso))
        self.assertEqual(combo.precio_publicado, "$ 300.00")

    def test_combo_rechaza_componentes_invalidos_y_descuentos_fuera_de_rango(self):
        agua = ProductoSimple("Agua", 100, 1, self.bebidas)
        queso = ProductoSimple("Queso", 200, 1, self.almacen)
        args = ("Combo", [agua, queso], 0.1, 1, self.bebidas)
        invalid_components = ["agua", [agua], [agua, object()]]
        for components in invalid_components:
            with self.subTest(components=components), self.assertRaises(ErrorDominio):
                ProductoCombo("Combo", components, 0.1, 1, self.bebidas)
        for discount in (True, "0.1", math.nan, -0.1, 1, math.inf):
            with self.subTest(discount=discount), self.assertRaises(ErrorDominio):
                ProductoCombo(args[0], args[1], discount, args[3], args[4])

    def test_destacado_valida_producto_y_orden(self):
        producto = ProductoSimple("Agua", 10, 1, self.bebidas)
        destacado = ProductoDestacado(producto, 1)
        self.assertIs(destacado.producto, producto)
        self.assertEqual(destacado.orden_vidriera, 1)
        with self.assertRaises(ErrorDominio):
            ProductoDestacado(object(), 1)
        for orden in (True, 1.5, 0):
            with self.subTest(orden=orden), self.assertRaises(ErrorDominio):
                ProductoDestacado(producto, orden)


if __name__ == "__main__":
    unittest.main()
