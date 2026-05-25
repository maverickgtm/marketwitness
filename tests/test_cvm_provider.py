import unittest
from datetime import date
from pathlib import Path

from targetaudit.providers.cvm import (
    CvmDataError,
    load_cvm_snapshot,
    parse_cvm_csv,
    render_cvm_html,
    render_cvm_report,
)


class CvmProviderTests(unittest.TestCase):
    def test_filters_equity_offerings_from_synthetic_fixture(self) -> None:
        offerings = load_cvm_snapshot(
            Path("data/samples/cvm-equity-offerings-synthetic.csv"),
            date(2026, 5, 25),
            date(2026, 5, 1),
        )
        report = render_cvm_report(
            offerings, date(2026, 5, 25), date(2026, 5, 1), "synthetic_fixture"
        )
        page = render_cvm_html(
            offerings, date(2026, 5, 25), date(2026, 5, 1), "synthetic_fixture"
        )

        self.assertEqual(len(offerings), 2)
        self.assertEqual(offerings[0].status, "offering_recorded")
        self.assertEqual(offerings[1].status, "offering_closed")
        self.assertNotIn("Excluded Debt Demo", report)
        self.assertIn("Synthetic CVM-shaped fixture", report)
        self.assertIn("not official offering evidence", page)
        self.assertIn("does not confirm B3 listing", page)
        self.assertIn("Offering closed", page)
        self.assertNotIn("offering_closed", page)

    def test_supports_resolution_160_schema_and_equity_filter(self) -> None:
        content = (
            "Numero_Requerimento;Numero_Processo;Data_requerimento;Data_Registro;"
            "Data_Encerramento;Status_Requerimento;Valor_Mobiliario;Nome_Emissor;"
            "Tipo_Oferta;Rito_Requerimento\n"
            "1;SRE/SYNTH/001;20/05/2026;21/05/2026;;Registrada;Acoes;"
            "Demo Equity S.A.;PRIMARIA;Automatico\n"
            "2;SRE/SYNTH/002;21/05/2026;22/05/2026;;Registrada;Debentures;"
            "Demo Debt S.A.;PRIMARIA;Automatico\n"
            "3;SRE/SYNTH/003;22/05/2026;23/05/2026;;Registrada;"
            "Outros titulos de securitizacao;Demo Securitization S.A.;PRIMARIA;Automatico\n"
        )

        offerings = parse_cvm_csv(content, date(2026, 5, 25), date(2026, 5, 1))

        self.assertEqual([item.company_name for item in offerings], ["Demo Equity S.A."])

    def test_rejects_future_filing(self) -> None:
        content = (
            "Numero_Processo;Numero_Registro_Oferta;Tipo_Oferta;Tipo_Ativo;"
            "Nome_Emissor;Rito_Oferta;Data_Abertura_Processo;Data_Protocolo\n"
            "SYNTH;REG;Primaria;ACOES;Future Demo;RCVM;2026-05-26;2026-05-26\n"
        )

        with self.assertRaisesRegex(CvmDataError, "after observation date"):
            parse_cvm_csv(content, date(2026, 5, 25), date(2026, 5, 1))

    def test_ignores_incomplete_historical_equity_outside_requested_window(self) -> None:
        content = (
            "Numero_Processo;Numero_Registro_Oferta;Tipo_Oferta;Tipo_Ativo;"
            "Nome_Emissor;Rito_Oferta;Data_Abertura_Processo;Data_Protocolo\n"
            "OLD;;Primaria;ACOES;Old Incomplete Demo;;2020-01-01;2020-01-01\n"
            "NEW;REG;Primaria;ACOES;Current Demo;RCVM;2026-05-20;2026-05-20\n"
        )

        offerings = parse_cvm_csv(content, date(2026, 5, 25), date(2026, 5, 1))

        self.assertEqual([item.company_name for item in offerings], ["Current Demo"])

    def test_ignores_equity_without_date_because_window_cannot_be_proven(self) -> None:
        content = (
            "Numero_Processo;Numero_Registro_Oferta;Tipo_Oferta;Tipo_Ativo;"
            "Nome_Emissor;Rito_Oferta;Data_Abertura_Processo;Data_Protocolo\n"
            "UNDATED;REG;Primaria;ACOES;Undated Demo;RCVM;;\n"
        )

        offerings = parse_cvm_csv(content, date(2026, 5, 25), date(2026, 5, 1))

        self.assertEqual(offerings, [])

    def test_rejects_duplicate_offering_identity(self) -> None:
        content = (
            "Numero_Processo;Numero_Registro_Oferta;Tipo_Oferta;Tipo_Ativo;"
            "Nome_Emissor;Rito_Oferta;Data_Abertura_Processo;Data_Protocolo\n"
            "SYNTH;REG;Primaria;ACOES;Demo One;RCVM;2026-05-20;2026-05-20\n"
            "SYNTH2;REG;Primaria;ACOES;Demo Two;RCVM;2026-05-20;2026-05-20\n"
        )

        with self.assertRaisesRegex(CvmDataError, "duplicates offering ID"):
            parse_cvm_csv(content, date(2026, 5, 25), date(2026, 5, 1))


if __name__ == "__main__":
    unittest.main()
