"""oracle_requirements: la cobertura de requisitos como datos para un agente."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import oracle_mcp.server as mcp
from oracle_metalenguaje.nucleo.proyecto import Proyecto
from tests.test_mcp import _conversacion, _desenmarcar, _ejecutar

MEDIDA = """ninguno demo.alto:
    de pieza p
    donde p.alto > 400
    umbral <= 0 segun contrato porque "cuatro metros"
    ambito universal
    alcance "no mira la malla"
"""


def _requisito(rid: str, cuerpo: str) -> str:
    return f'requisito {rid}:\n    texto "t de {rid}"\n{cuerpo}'


class RequisitosTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.raiz))
        (self.raiz / "oracle.json").write_text(
            '{"esquema": "oracle.proyecto/v1", "catalogo_base": false, "perfiles": []}\n', encoding="utf-8")
        (self.raiz / "catalogos" / "demo").mkdir(parents=True)
        (self.raiz / "catalogos" / "demo" / "demo.alto.oracle").write_text(MEDIDA, encoding="utf-8")
        (self.raiz / "catalogos" / "demo" / "demo.ancho.oracle").write_text(
            MEDIDA.replace("demo.alto", "demo.ancho"), encoding="utf-8")

    def _escribir(self, **requisitos: str) -> None:
        (self.raiz / "requisitos").mkdir(exist_ok=True)
        for rid, cuerpo in requisitos.items():
            (self.raiz / "requisitos" / f"{rid}.requisito").write_text(_requisito(rid, cuerpo), encoding="utf-8")

    def test_sin_requisitos(self) -> None:
        r = mcp.requisitos_para_mcp(Proyecto(self.raiz), {})
        self.assertEqual(r["totales"], {"requisitos": 0, "total": 0, "parcial": 0, "ninguna": 0,
                                        "con_medidas_inexistentes": 0})
        self.assertEqual(r["medidas_sin_requisito"], ["demo.alto", "demo.ancho"])
        self.assertEqual(r["esquema"], "oracle.mcp/requisitos/v1")

    def test_cobertura_por_requisito(self) -> None:
        self._escribir(**{
            "p.medido": "    medido_por demo.alto\n",
            "p.parcial": '    medido_por demo.alto\n    sin_medir "la malla"\n',
            "p.nada": '    sin_medir "sólo en una terminal"\n',
            "p.roto": "    medido_por demo.fantasma\n",
        })
        r = mcp.requisitos_para_mcp(Proyecto(self.raiz), None)
        self.assertEqual(r["totales"], {"requisitos": 4, "total": 2, "parcial": 1, "ninguna": 1,
                                        "con_medidas_inexistentes": 1})
        por_id = {f["id"]: f for f in r["requisitos"]}
        self.assertEqual(por_id["p.parcial"], {
            "id": "p.parcial", "texto": "t de p.parcial", "fuente": "", "cobertura": "parcial",
            "medido_por": ["demo.alto"], "sin_medir": "la malla", "medidas_inexistentes": []})
        self.assertEqual(por_id["p.roto"]["medidas_inexistentes"], ["demo.fantasma"])
        self.assertEqual(r["medidas_sin_requisito"], ["demo.ancho"])

    def test_errores_explicitos(self) -> None:
        with self.assertRaises(mcp.ErrorHerramienta) as ctx:
            mcp.requisitos_para_mcp(Proyecto(self.raiz), {"ids": ["x"]})
        self.assertEqual(ctx.exception.codigo, "ARGUMENTOS_INVALIDOS")
        self._escribir(**{"p.mal": ""})
        with self.assertRaises(mcp.ErrorHerramienta) as ctx:
            mcp.requisitos_para_mcp(Proyecto(self.raiz), {})
        self.assertEqual(ctx.exception.codigo, "REQUISITO_INVALIDO")
        self.assertIn("No se devolvió una cobertura parcial", str(ctx.exception))

    def test_catalogo_roto_y_escalares_sin_confianza(self) -> None:
        (self.raiz / "catalogos" / "demo" / "demo.ancho.oracle").write_text("ninguno roto\n", encoding="utf-8")
        with self.assertRaises(mcp.ErrorHerramienta) as ctx:
            mcp.requisitos_para_mcp(Proyecto(self.raiz), {})
        self.assertEqual(ctx.exception.codigo, "CATALOGO_INVALIDO")
        (self.raiz / "catalogos" / "demo" / "demo.ancho.oracle").unlink()
        (self.raiz / "escalares.py").write_text("x = 1\n", encoding="utf-8")
        with self.assertRaises(mcp.ErrorHerramienta) as ctx:
            mcp.requisitos_para_mcp(Proyecto(self.raiz), {})
        self.assertNotEqual(ctx.exception.codigo, "CATALOGO_INVALIDO")

    def test_por_el_protocolo(self) -> None:
        self._escribir(**{"p.medido": "    medido_por demo.alto\n"})
        corrida = _ejecutar(self.raiz, _conversacion({
            "jsonrpc": "2.0", "id": 7, "method": "tools/call",
            "params": {"name": "oracle_requirements", "arguments": {}}}))
        respuesta = next(m for m in _desenmarcar(corrida.stdout) if m.get("id") == 7)
        self.assertFalse(respuesta["result"]["isError"])
        contenido = respuesta["result"]["structuredContent"]
        self.assertEqual(contenido["totales"]["total"], 1)
        self.assertEqual(json.loads(respuesta["result"]["content"][0]["text"]), contenido)


if __name__ == "__main__":
    unittest.main()
