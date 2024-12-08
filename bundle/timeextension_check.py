import subprocess
from os import path
import sys
import json
import os
import stat
from datetime import datetime, timedelta
import time

username = None
try:
    username = sys.argv[2]
    os.makedirs(path.expandvars("%APPDATA%\\TimeextensionData"), exist_ok=True)
    sendto_dir = path.expandvars("%APPDATA%\\TimeextensionData\\database.json")
except Exception as e:
    print(e)
    sys.exit(1)

weekday_dict = {
    0: "segunda",
    1: "terca",
    2: "quarta",
    3: "quinta",
    4: "sexta",
    5: "sabado",
    6: "domingo",
}

weekday_windows_sch_dict = {
    "segunda": "MON",
    "terca": "TUE",
    "quarta": "WED",
    "quinta": "THU",
    "sexta": "FRI",
    "sabado": "SAT",
    "domingo": "SUN",
}


def fetch():
    output = subprocess.check_output(
        [
            "curl",
            "https://drive.usercontent.google.com/download?id=13k6XUuACSFzh_2f_QU-H3peRQAOP21BB&export=download&authuser=0&confirm=t&uuid=424253ef-908c-44b6-be9d-809e52cb59dd&at=APZUnTUbz4Bw_ZzgWvR4PfkhvL5Z:1718835566402",
        ]
    )

    timetable = json.loads(output)
    create_schedule = False
    try:
        with open(sendto_dir, "r") as f:
            old_timetable = json.loads(f.read())
            create_schedule = (
                False if timetable["versao"] == old_timetable["versao"] else True
            )
    except Exception as e:
        create_schedule = True
        print(e)

    if timetable is not None:
        with open(sendto_dir, "w") as f:
            f.write(json.dumps(timetable))

    os.chmod(sendto_dir, stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    if create_schedule:
        build_schedule()


def build_schedule():
    print("building schedule")
    with open(sendto_dir, "r") as f:
        schedule = json.loads(f.read())
        for dia_da_semana in [
            "segunda",
            "terca",
            "quarta",
            "quinta",
            "sexta",
            "sabado",
            "domingo",
        ]:
            for item in schedule["agenda"][dia_da_semana]:
                hora_fim = datetime.strptime(item["fim"], "%H:%M:%S")
                command = [
                    "schtasks",
                    "/create",
                    "/tn",
                    item["nome"],
                    "/tr",
                    '"shutdown /f"',
                    "/sc",
                    "weekly",
                    "/mo",
                    "1",
                    "/d",
                    weekday_windows_sch_dict[dia_da_semana],
                    "/st",
                    f"{str(hora_fim.hour).zfill(2)}:{str(hora_fim.minute).zfill(2)}",
                    "/ru",
                    '"{username}"',
                    "/f",
                ]
                print("executing command: " + str(command))
                subprocess_run(command)


def check():
    hoje = datetime_now()
    hour, minute = (hoje.hour, hoje.minute)
    hora_base = datetime.strptime(f"{hour}:{minute}:00", "%H:%M:%S")
    desligar_fora_do_horario = hora_base + timedelta(minutes=10)
    day_of_week = weekday_dict[hoje.weekday()]
    with open(sendto_dir, "r") as f:
        timetable = json.loads(f.read())
        for schedule in timetable["agenda"][day_of_week]:
            a = datetime.strptime(schedule["inicio"], "%H:%M:%S") - timedelta(
                minutes=10
            )  # permitir entrada adiantada
            b = datetime.strptime(schedule["fim"], "%H:%M:%S")
            delta_proxima_agenda = (a - hora_base).total_seconds()
            delta_encerramento = (b - hora_base).total_seconds()
            if delta_proxima_agenda < 0 and delta_encerramento > 0:
                print("delete agendamento fora do horario")
                try:
                    subprocess_run(
                        [
                            "schtasks",
                            "/delete",
                            "/tn",
                            "DesligamentoForaDoHorario",
                            "/ru",
                            '"{username}"',
                            "/f",
                        ]
                    )
                except Exception as e:
                    pass
                return

    agendar_desligar_fora_do_horario(desligar_fora_do_horario)


def agendar_desligar_fora_do_horario(desligar_fora_do_horario):
    subprocess_run(
        [
            "msg",
            "*",
            f"Fora do horário estabelecido. Desligamento agendado para {str(desligar_fora_do_horario.hour).zfill(2)}:{str(desligar_fora_do_horario.minute).zfill(2)}",
        ]
    )
    subprocess_run(
        [
            "schtasks",
            "/create",
            "/tn",
            "DesligamentoForaDoHorario",
            "/tr",
            '"shutdown /f"',
            "/sc",
            "ONCE",
            "/st",
            f"{str(desligar_fora_do_horario.hour).zfill(2)}:{str(desligar_fora_do_horario.minute).zfill(2)}",
            "/ru",
            '"{username}"',
            "/f",
        ]
    )


def subprocess_run(args):
    print("executing command: " + str(args))
    process_result = subprocess.run(args, text=True, capture_output=True)
    if process_result.returncode != 0:
        print(process_result.stderr)
        raise Exception(process_result.stderr)
    return process_result


def datetime_now():
    return datetime.now()


if __name__ == "__main__":
    try:
        if sys.argv[1] == "fetch":
            fetch()
        elif sys.argv[1] == "check":
            try:
                fetch()
            except Exception as e:
                print(e)
            check()
    except Exception as e:
        print(e)
        sys.exit(1)
