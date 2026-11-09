"""Prueba aislada de búsqueda parcial del adaptador MongoDB."""

import unittest
from unittest.mock import MagicMock

from adapters.laboratorio_mongo import LaboratorioMongoAdapter


class MongoNameSearchTest(unittest.TestCase):
    def test_busqueda_parcial_nointerpreta_regex_del_usuario(self):
        cursor = MagicMock()
        cursor.sort.return_value = cursor
        cursor.limit.return_value = cursor
        cursor.__iter__.return_value = iter([
            {
                "_id": "synthetic-id",
                "nombre": "María Ana Demo",
                "dpi": "0000000000001",
                "fecha_nacimiento": "1990-02-03",
                "estado": "activo",
            }
        ])
        collection = MagicMock()
        collection.find.return_value = cursor
        database = {"pacientes": collection}
        client = MagicMock()
        client.__getitem__.side_effect = lambda _name: database

        adapter = LaboratorioMongoAdapter()
        adapter.client = client
        resultados = adapter.buscar_pacientes_por_nombre("ana.*")

        collection.find.assert_called_once_with({
            "nombre": {"$regex": r"ana\.\*", "$options": "i"}
        })
        self.assertEqual([resultado.nombre for resultado in resultados], ["María Ana Demo"])
        self.assertEqual(resultados[0].dpi, "0000000000001")


if __name__ == "__main__":
    unittest.main()
