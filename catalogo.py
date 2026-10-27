"""Modelo en memoria del catálogo de Food Store."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import isfinite
from numbers import Real
from typing import Protocol, Sequence


class ErrorDominio(ValueError):
    """Error para datos que no respetan las reglas del catálogo."""


@dataclass(frozen=True)
class UnidadMedida:
    nombre: str
    simbolo: str
    tipo: str

    def __post_init__(self) -> None:
        valores = (self.nombre, self.simbolo, self.tipo)
        if not all(isinstance(valor, str) and valor.strip() for valor in valores):
            raise ErrorDominio(
                "La unidad, el símbolo y el tipo no pueden estar vacíos."
            )


class Exportable(Protocol):
    def exportar(self) -> str: ...


def exportar_catalogo(items: list[Exportable]) -> list[str]:
    return [item.exportar() for item in items]


class Categoria:
    def __init__(self, nombre: str, descripcion: str = "") -> None:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorDominio("El nombre de la categoría no puede estar vacío.")
        if not isinstance(descripcion, str):
            raise ErrorDominio("La descripción debe ser texto.")
        self._nombre = nombre.strip()
        self._descripcion = descripcion

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def descripcion(self) -> str:
        return self._descripcion


class ProductoCategoria:
    """Vínculo creado y administrado únicamente por su Producto."""

    def __init__(self, categoria: Categoria, es_principal: bool) -> None:
        self._categoria = categoria
        self._es_principal = es_principal

    @property
    def categoria(self) -> Categoria:
        return self._categoria

    @property
    def es_principal(self) -> bool:
        return self._es_principal

    def _marcar_principal(self, valor: bool) -> None:
        self._es_principal = valor


class Producto(ABC):
    def __init__(
        self,
        nombre: str,
        precio_base: float,
        stock_cantidad: float,
        categoria_principal: Categoria,
        unidad_venta: UnidadMedida | None = None,
        habilitado: bool = True,
    ) -> None:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorDominio("El nombre del producto no puede estar vacío.")
        self._validar_no_negativo(precio_base, "El precio base")
        self._validar_no_negativo(stock_cantidad, "El stock")
        if not isinstance(categoria_principal, Categoria):
            raise ErrorDominio("La categoría principal debe ser una Categoria.")
        if unidad_venta is not None and not isinstance(unidad_venta, UnidadMedida):
            raise ErrorDominio("La unidad de venta debe ser una UnidadMedida o None.")
        if not isinstance(habilitado, bool):
            raise ErrorDominio("El estado habilitado debe ser booleano.")
        self._nombre = nombre.strip()
        self._precio_base = float(precio_base)
        self._stock_cantidad = float(stock_cantidad)
        self._habilitado = habilitado
        self._unidad_venta = unidad_venta
        self._clasificaciones = [ProductoCategoria(categoria_principal, True)]

    @staticmethod
    def _validar_no_negativo(valor: Real, etiqueta: str) -> None:
        if (
            isinstance(valor, bool)
            or not isinstance(valor, Real)
            or not isfinite(valor)
            or valor < 0
        ):
            raise ErrorDominio(
                f"{etiqueta} debe ser un número finito mayor o igual a cero."
            )

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @property
    def unidad_venta(self) -> UnidadMedida | None:
        return self._unidad_venta

    @property
    def disponible(self) -> bool:
        return self._habilitado and self._stock_cantidad > 0

    @property
    def precio_publicado(self) -> str:
        precio = f"$ {self._precio_base:.2f}"
        if self._unidad_venta:
            return f"{precio} / {self._unidad_venta.simbolo}"
        return precio

    def habilitar(self) -> None:
        self._habilitado = True

    def deshabilitar(self) -> None:
        self._habilitado = False

    def clasificar_en(self, categoria: Categoria, es_principal: bool = False) -> None:
        if not isinstance(categoria, Categoria):
            raise ErrorDominio("La clasificación debe referirse a una Categoria.")
        if any(vinculo.categoria is categoria for vinculo in self._clasificaciones):
            raise ErrorDominio(
                f"El producto ya está clasificado en {categoria.nombre}."
            )
        if not isinstance(es_principal, bool):
            raise ErrorDominio("es_principal debe ser booleano.")
        if es_principal:
            for vinculo in self._clasificaciones:
                vinculo._marcar_principal(False)
        self._clasificaciones.append(ProductoCategoria(categoria, es_principal))

    def categorias(self) -> tuple[ProductoCategoria, ...]:
        return tuple(self._clasificaciones)

    def categoria_principal(self) -> Categoria:
        return next(v.categoria for v in self._clasificaciones if v.es_principal)

    @abstractmethod
    def precio_final(self, cantidad: float) -> float:
        """Calcula el importe para la cantidad solicitada."""

    def exportar(self) -> str:
        return (
            f"PRODUCTO|{self._nombre}|{self.precio_publicado}|"
            f"{self.categoria_principal().nombre}"
        )


def _validar_cantidad_entera(cantidad: float) -> None:
    if (
        isinstance(cantidad, bool)
        or not isinstance(cantidad, Real)
        or not isfinite(cantidad)
        or cantidad < 1
        or not float(cantidad).is_integer()
    ):
        raise ErrorDominio("La cantidad debe ser un entero mayor o igual a uno.")


class ProductoSimple(Producto):
    def precio_final(self, cantidad: float) -> float:
        _validar_cantidad_entera(cantidad)
        return self._precio_base * cantidad


class ProductoPorPeso(Producto):
    def precio_final(self, cantidad: float) -> float:
        if (
            isinstance(cantidad, bool)
            or not isinstance(cantidad, Real)
            or not isfinite(cantidad)
            or cantidad <= 0
        ):
            raise ErrorDominio("El peso debe ser un número finito mayor que cero.")
        return round(self._precio_base * cantidad, 2)


class ProductoCombo(Producto):
    def __init__(
        self,
        nombre: str,
        componentes: Sequence[Producto],
        descuento: float,
        stock_cantidad: float,
        categoria_principal: Categoria,
        unidad_venta: UnidadMedida | None = None,
        habilitado: bool = True,
    ) -> None:
        if isinstance(componentes, (str, bytes)):
            raise ErrorDominio("Los componentes deben ser productos ya construidos.")
        componentes_copiados = list(componentes)
        if len(componentes_copiados) < 2:
            raise ErrorDominio("Un combo necesita al menos dos componentes.")
        if any(
            not isinstance(componente, Producto)
            for componente in componentes_copiados
        ):
            raise ErrorDominio("Cada componente debe ser un Producto.")
        if (
            isinstance(descuento, bool)
            or not isinstance(descuento, Real)
            or not isfinite(descuento)
            or not 0 <= descuento < 1
        ):
            raise ErrorDominio(
                "El descuento debe estar entre cero inclusive y uno exclusivo."
            )
        self._componentes = componentes_copiados
        self._descuento = float(descuento)
        precio_base = sum(
            componente.precio_final(1) for componente in componentes_copiados
        )
        super().__init__(
            nombre,
            precio_base,
            stock_cantidad,
            categoria_principal,
            unidad_venta,
            habilitado,
        )

    def componentes(self) -> tuple[Producto, ...]:
        return tuple(self._componentes)

    def precio_final(self, cantidad: float) -> float:
        _validar_cantidad_entera(cantidad)
        precio_componentes = sum(
            componente.precio_final(1) for componente in self._componentes
        )
        return precio_componentes * (1 - self._descuento) * cantidad


class ProductoDestacado:
    """Dato promocional asociado a cualquier producto del catálogo."""

    def __init__(self, producto: Producto, orden_vidriera: int) -> None:
        if not isinstance(producto, Producto):
            raise ErrorDominio("Solo se pueden destacar productos del catálogo.")
        if (
            isinstance(orden_vidriera, bool)
            or not isinstance(orden_vidriera, int)
            or orden_vidriera < 1
        ):
            raise ErrorDominio(
                "El orden de vidriera debe ser un entero mayor o igual a uno."
            )
        self._producto = producto
        self._orden_vidriera = orden_vidriera

    @property
    def producto(self) -> Producto:
        return self._producto

    @property
    def orden_vidriera(self) -> int:
        return self._orden_vidriera
