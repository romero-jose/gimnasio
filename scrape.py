from datetime import date
import requests
import bs4 as bs
import os

CREDENTIAL_FILE = "credentials.json"
BASE_URL = "https://ucampus.uchile.cl"
URL = f"{BASE_URL}/m/fcfm_reservas/detalle"
LOGIN_URL = f"{BASE_URL}/upasaporte/adi"


def weekday(i: int) -> int:
    weekdays = [
        "Lunes",
        "Martes",
        "Miercoles",
        "Jueves",
        "Viernes",
        "Sabado",
        "Domingo",
    ]
    if i >= 7:
        raise Exception("Weekday index out of range")
    return weekdays[i]


def get_credentials() -> dict[str, str]:
    user = os.environ["USER"]
    password = os.environ["PASSWORD"]
    return {
        "user": user,
        "password": password,
    }


def login(user: str, password: str):
    s = requests.Session()

    data = {
        "servicio": "fcfm",
        "debug": "0",
        "extras[_LB]": "ucampus81-int",
        "extras[lang]": "es",
        "extras[recordar]": "1",
        "recordar": "1",
        "username": user,
        "password": password,
    }

    s.post(LOGIN_URL, data=data)

    return s


def fetch(date: date, s: requests.Session) -> str:
    response = s.get(URL, params={"id": 70, "fecha": date.isoformat()})
    with open("page.html", "w") as f:
        html = f.write(response.text)
    return response.text


def fetch_from_file(_: str) -> str:
    with open("page.html", "r") as f:
        html = f.read()
    return html


def extract(html: str):
    soup = bs.BeautifulSoup(html, features="html.parser")
    table = soup.find("table", attrs={"class": "dhorario"})
    tbody = table.find("tbody")
    tcols = tbody.find_all("td")
    data = []
    for i, col in enumerate(tcols):
        rows = col.select("div.bloque.rainbow")
        for r in rows:
            dia = i
            horario = r.find("h1").text
            cupos = r.find("h2").text
            enlace = f"{URL}/{r.find('a')['href']}"

            data.append(
                {
                    "dia": dia,
                    "horario": horario,
                    "cupos": cupos,
                    "enlace": enlace,
                }
            )
    return data


def format_data(data):
    msg = []
    for d in data:
        msg.append(f"|=========================================|")
        msg.append(f"| Dia:     {weekday(d['dia'])}")
        msg.append(f"| Horario: {d['horario']}")
        msg.append(f"| Cupos:   {d['cupos']}")
        msg.append(f"| Enlace:  {d['enlace']}")

    if not data:
        msg.append("No hay horarios para hoy :(")

    return "\n".join(msg)

def fetch_formatted_data():
    credentials = get_credentials()
    authenticated_session = login(
        user=credentials["user"], password=credentials["password"]
    )
    html = fetch(date=date.today(), s=authenticated_session)
    data = extract(html)
    formatted_data = format_data(data)
    return formatted_data
