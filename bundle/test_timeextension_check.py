import timeextension_check
from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch


class TestTimeExtension(TestCase):
    def test_dentro_do_horario(self):
        timeextension_check.datetime_now = Mock(
            return_value=datetime.strptime(f"10:00:00", "%H:%M:%S")
        )
        timeextension_check.subprocess_run = Mock()
        timeextension_check.check()

        self.assertListEqual(
            timeextension_check.subprocess_run.mock_calls[0].args[0],
            ["schtasks", "/delete", "/tn", "DesligamentoForaDoHorario", "/f"],
        )

    def test_antes_do_horario(self):
        timeextension_check.datetime_now = Mock(
            return_value=datetime.strptime(f"13:00:00", "%H:%M:%S")
        )
        timeextension_check.subprocess_run = Mock()
        timeextension_check.check()

        self.assertListEqual(
            timeextension_check.subprocess_run.mock_calls[0].args[0],
            [
                "msg",
                "*",
                "Fora do horário estabelecido. Desligamento agendado para 13:10",
            ],
        )
        self.assertListEqual(
            timeextension_check.subprocess_run.mock_calls[1].args[0],
            [
                "schtasks",
                "/create",
                "/tn",
                "DesligamentoForaDoHorario",
                "/tr",
                "shutdown /f",
                "/sc",
                "ONCE",
                "/st",
                "13:10",
                "/f",
            ],
        )

    def test_fim_do_dia(self):
        timeextension_check.datetime_now = Mock(
            return_value=datetime.strptime(f"23:31:00", "%H:%M:%S")
        )
        timeextension_check.subprocess_run = Mock()
        timeextension_check.check()

        self.assertListEqual(
            timeextension_check.subprocess_run.mock_calls[0].args[0],
            [
                "msg",
                "*",
                "Fora do horário estabelecido. Desligamento agendado para 23:41",
            ],
        )
        self.assertListEqual(
            timeextension_check.subprocess_run.mock_calls[1].args[0],
            [
                "schtasks",
                "/create",
                "/tn",
                "DesligamentoForaDoHorario",
                "/tr",
                "shutdown /f",
                "/sc",
                "ONCE",
                "/st",
                "23:41",
                "/f",
            ],
        )
