"""Prueba de lógica del adaptador Firestore sin credenciales ni red.

No sustituye la prueba de integración contra Firestore real.
Ejecutar: python -m unittest tests.test_firestore_adapter -v
"""

import copy
import unittest
import uuid

from google.cloud import firestore

from adapters.odontologia_firebase import OdontologiaFirebaseAdapter
from core.errors import ClinicalConflictError
from core.models import (
    CitaCambioIn, CitaIn, ConsultaIn, DiagnosticoIn, PacienteIn,
    ProcedimientoDentalIn, RecetaIn, TratamientoIn,
)


class FakeSnapshot:
    def __init__(self, ref, data):
        self.id = ref.id
        self.reference = ref
        self._data = copy.deepcopy(data)
        self.exists = data is not None

    def to_dict(self):
        return copy.deepcopy(self._data)


class FakeDocument:
    def __init__(self, db, collection, doc_id):
        self.db, self.collection, self.id = db, collection, doc_id

    @property
    def key(self):
        return self.collection, self.id

    def get(self):
        return FakeSnapshot(self, self.db.data.get(self.key))

    def set(self, value):
        self.db.data[self.key] = copy.deepcopy(value)

    def update(self, changes):
        if self.key not in self.db.data:
            raise ValueError("Documento inexistente")
        for key, value in changes.items():
            if isinstance(value, firestore.ArrayUnion):
                self.db.data[self.key].setdefault(key, []).extend(copy.deepcopy(value._values))
            else:
                self.db.data[self.key][key] = copy.deepcopy(value)


class FakeQuery:
    def __init__(self, db, collection, condition=None, max_items=None):
        self.db, self.collection = db, collection
        self.condition, self.max_items = condition, max_items

    def where(self, filter):
        return FakeQuery(self.db, self.collection, filter, self.max_items)

    def limit(self, n):
        return FakeQuery(self.db, self.collection, self.condition, n)

    def get(self):
        result = []
        for (collection, doc_id), data in self.db.data.items():
            if collection != self.collection:
                continue
            if self.condition and data.get(self.condition.field_path) != self.condition.value:
                continue
            result.append(FakeSnapshot(FakeDocument(self.db, collection, doc_id), data))
        return result[:self.max_items]


class FakeCollection(FakeQuery):
    def document(self, doc_id=None):
        return FakeDocument(self.db, self.collection, doc_id or uuid.uuid4().hex)


class FakeBatch:
    def __init__(self):
        self.pending = []

    def set(self, ref, value):
        self.pending.append((ref, value))

    def commit(self):
        for ref, value in self.pending:
            ref.set(value)


class FakeFirestore:
    def __init__(self):
        self.data = {}

    def collection(self, name):
        return FakeCollection(self, name)

    def batch(self):
        return FakeBatch()


class FirestoreAdapterTest(unittest.TestCase):
    def test_historial_odontologico_completo(self):
        adapter = OdontologiaFirebaseAdapter(client=FakeFirestore())
        p = adapter.registrar_paciente(PacienteIn(
            nombre="Paciente sintético", dpi="1234567890123",
            fecha_nacimiento="1990-02-03",
        ))
        cita = adapter.registrar_cita(CitaIn(
            id_paciente=p.id_paciente, fecha="2026-12-10T10:00:00",
            servicio="Limpieza",
        ))
        changed = adapter.cambiar_cita(cita["id_cita"], CitaCambioIn(estado="cancelada"))
        self.assertEqual(changed["estado"], "cancelada")
        consulta = adapter.registrar_consulta(ConsultaIn(
            id_paciente=p.id_paciente, motivo="Dolor dental",
        ))
        cid = consulta.id_consulta
        adapter.agregar_diagnostico(DiagnosticoIn(
            id_consulta=cid, descripcion="Caries", codigo_cie10="K02.9",
        ))
        adapter.registrar_tratamiento(TratamientoIn(
            id_consulta=cid, descripcion="Restauración",
        ))
        adapter.recetar_medicamento(RecetaIn(
            id_consulta=cid, medicamento="Medicamento de prueba",
            dosis="1", frecuencia="Diario", duracion_dias=2,
        ))
        adapter.registrar_procedimiento(ProcedimientoDentalIn(
            id_consulta=cid, pieza="36", procedimiento="Resina oclusal",
        ))
        history = adapter.get_historial(p.id_paciente)
        for field in ("citas", "consultas", "diagnosticos", "tratamientos",
                      "recetas", "procedimientos_dentales"):
            self.assertGreaterEqual(len(getattr(history, field)), 1, field)
        self.assertTrue(adapter.archivar_historial(p.id_paciente))
        with self.assertRaises(ClinicalConflictError):
            adapter.registrar_consulta(ConsultaIn(
                id_paciente=p.id_paciente, motivo="Debe bloquearse",
            ))


if __name__ == "__main__":
    unittest.main()
