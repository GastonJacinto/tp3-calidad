"""Demostración de las decisiones de diseño del catálogo."""

from catalogo import (
    Categoria,
    Producto,
    ProductoCombo,
    ProductoDestacado,
    ProductoPorPeso,
    ProductoSimple,
    UnidadMedida,
    exportar_catalogo,
)
from libreria_externa import FichaPuntoDeVenta


def main() -> None:
    bebidas = Categoria("Bebidas", "Productos para tomar")
    almacen = Categoria("Almacén", "Productos envasados")
    fiambrería = Categoria("Fiambrería")
    unidad = UnidadMedida("unidad", "u", "unidad")
    kilogramo = UnidadMedida("kilogramo", "kg", "masa")

    agua = ProductoSimple("Agua mineral", 1200, 20, bebidas, unidad)
    gaseosa = ProductoSimple("Gaseosa", 1800, 12, bebidas, unidad)
    queso = ProductoPorPeso("Queso", 9500, 8, fiambrería, kilogramo)
    agua.clasificar_en(almacen)
    agua.clasificar_en(fiambrería, es_principal=True)

    merienda = ProductoCombo("Combo merienda", [gaseosa, queso], 0.15, 4, almacen)
    segundo_combo = ProductoCombo("Combo familiar", [merienda, agua], 0.1, 2, bebidas)
    destacados = [ProductoDestacado(gaseosa, 1), ProductoDestacado(segundo_combo, 2)]

    print("CATÁLOGO FOOD STORE")
    for producto in (agua, gaseosa, queso, merienda, segundo_combo):
        print(
            f"- {producto.nombre}: {producto.precio_publicado}; "
            f"precio por cantidad: ${producto.precio_final(2):.2f}; "
            f"categoría principal: {producto.categoria_principal().nombre}; "
            f"disponible: {producto.disponible}"
        )

    print("\nDestacados:")
    for destacado in destacados:
        print(f"{destacado.orden_vidriera}. {destacado.producto.nombre}")

    agua.deshabilitar()
    print(f"\nAgua deshabilitada, disponible={agua.disponible}")
    agua.habilitar()
    print(f"Agua habilitada, disponible={agua.disponible}")

    items = [
        agua,
        gaseosa,
        queso,
        merienda,
        segundo_combo,
        FichaPuntoDeVenta("PV-01", "Caja principal"),
    ]
    print("\nExportación conjunta:")
    for linea in exportar_catalogo(items):
        print(linea)

    print("\nEvidencia de composición y agregación:")
    print(f"El combo conserva a {merienda.componentes()[0].nombre} como componente.")
    print(
        "Agua sigue existiendo y puede estar en otro combo: "
        f"{agua in segundo_combo.componentes()}."
    )
    vinculos = [(v.categoria.nombre, v.es_principal) for v in agua.categorias()]
    print(f"Clasificaciones internas (categoría, principal): {vinculos}")

    try:
        Producto("Producto abstracto", 100, 1, bebidas)
    except TypeError as error:
        print(f"\nFalla temprana ABC: {error}")

    class ProductoIncompleto(Producto):
        pass

    try:
        ProductoIncompleto("Producto incompleto", 100, 1, bebidas)
    except TypeError as error:
        print(f"Falla temprana de subclase: {error}")


if __name__ == "__main__":
    main()
