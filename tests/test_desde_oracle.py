"""Los tests del MCP que vivían en otros archivos de Oracle, traídos al separarlo.

Vienen de tests/test_auditoria_ronda2.py, test_ensenanza_una_sintaxis.py,
test_forma_unica_texto.py y test_relacion_duplicada.py de Oracle 0.33.0.
"""
from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import oracle_metalenguaje
from oracle_metalenguaje.nucleo.proyecto import Proyecto
from oracle_metalenguaje.tools import cli
from oracle_mcp import server as mcp
from tests.test_mcp import _conversacion, _desenmarcar, _medida, _pedido_evaluar, _proyecto

RELACIONES_DE_ORACLE = Path(oracle_metalenguaje.__file__).resolve().parent / "relaciones"

MEDIDA = ('medida demo.uno:\n'
          '    de item i\n'
          '    resumen contar(1)\n'
          '    umbral <= 0 segun contrato porque "ningún item ofensivo"\n'
          '    ambito universal\n'
          '    alcance "NO ve propiedades distintas de la presencia del item"\n')


class NoAplicadasTests(unittest.TestCase):
    def test_no_aprueba_si_una_medida_propia_quedo_sin_aplicar(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            (raiz / "oracle.json").write_text(json.dumps({
                "esquema": "oracle.proyecto/v1", "catalogo_base": False, "perfiles": [],
            }))
            for nombre, relacion in (("uno", "item"), ("dos", "otro")):
                (raiz / "catalogos" / f"{nombre}.oracle").write_text(
                    f"medida demo.{nombre}:\n"
                    f"    de {relacion} i\n"
                    '    resumen contar(1)\n'
                    '    umbral >= 0 segun contrato porque "conteo"\n'
                    '    ambito universal\n'
                    '    alcance "conteo"\n')
            evidencia = {"item": [{"id": 1}]}
            ruta_evidencia = raiz / "e.json"
            ruta_evidencia.write_text(json.dumps(evidencia))
            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main(["juzgar", "--proyecto", str(raiz), "--con",
                               str(ruta_evidencia), "--json"])
            self.assertEqual(rc, 1)
            self.assertIs(json.loads(salida.getvalue())["ok"], False)

            resultado = mcp.juzgar_para_mcp(Proyecto(raiz), {"evidencia": evidencia})
            self.assertEqual(resultado["no_aplicadas"], [{"id": "demo.dos", "faltan": ["otro"]}])
            self.assertIs(resultado["ok"], False)


class UnaSolaSintaxisTests(unittest.TestCase):
    def test_solo_recibe_medidas_en_superficie(self):
        for herramienta in mcp.HERRAMIENTAS:
            esquema = herramienta["inputSchema"]["properties"].get("medida")
            if esquema is not None:
                por_texto = next(rama for rama in esquema["oneOf"]
                                 if "texto" in rama["properties"])
                self.assertEqual(por_texto["properties"]["formato"], {"const": "oracle"})
        with self.assertRaises(mcp.ErrorHerramienta):
            mcp._validar_evaluacion({"medida": {"texto": '["medida"]', "formato": "json"},
                                    "evidencia": {}})

    def test_rechaza_variantes_crlf_y_sin_salto_final(self):
        for texto in (MEDIDA.replace("medida demo", "medida   demo"),
                      MEDIDA.replace("\n", "\r\n"), MEDIDA.rstrip("\n")):
            with self.subTest(texto=texto[:30]):
                with self.assertRaises(mcp.ErrorHerramienta) as ctx:
                    mcp._medida_en_memoria({"texto": texto, "formato": "oracle"}, None)
                self.assertIn("fuera de la forma única", str(ctx.exception))


class RelacionDuplicadaTests(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = _proyecto(Path(temporal.name), _medida("demo.uno"))
        (self.raiz / "oracle.json").write_text(
            '{"esquema": "oracle.proyecto/v1", "catalogo_base": true}', encoding="utf-8")
        for nombre in ("corpus", "diferencial", "relaciones"):
            (self.raiz / nombre).mkdir()
        shutil.copy(RELACIONES_DE_ORACLE / "pieza.relacion", self.raiz / "relaciones/pieza.relacion")

    def test_una_relacion_que_ya_es_de_oracle_es_error_de_la_llamada(self):
        entrada = _conversacion(_pedido_evaluar(2, {
            "medida": {"id": "demo.uno"}, "evidencia": {"item": []}}))
        salida = io.BytesIO()
        codigo = mcp.servir(Proyecto(self.raiz), io.BytesIO(entrada), salida)
        self.assertEqual(codigo, 0)  # El error pertenece a la llamada, no al transporte.
        resultado = _desenmarcar(salida.getvalue())[1]["result"]
        self.assertTrue(resultado["isError"])
        texto = resultado["content"][0]["text"]
        self.assertIn("PROYECTO_INVALIDO —", texto)
        self.assertIn("pieza", texto)
        self.assertIn(str(self.raiz / "relaciones/pieza.relacion"), texto)
        self.assertIn("ya existe en Oracle", texto)
        self.assertNotIn("Traceback", texto)


if __name__ == "__main__":
    unittest.main()
