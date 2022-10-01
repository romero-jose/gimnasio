import os
import uuid
from datetime import date, datetime, time, timedelta

import bs4 as bs
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://ucampus.uchile.cl"
URL = f"{BASE_URL}/m/fcfm_reservas/detalle"
LOGIN_URL = f"{BASE_URL}/upasaporte/adi"

USER = os.environ["USER"]
PASSWORD = os.environ["PASSWORD"]


def get_credentials() -> dict[str, str]:
    user = USER
    password = PASSWORD
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
        f.write(response.text)
    return response.text


def fetch_from_file(_: str) -> str:
    with open("page.html", "r") as f:
        html = f.read()
    return html


def get_user_uuid_from_image_url(url: str) -> str:
    """
    Attempts to obtain the user uuid from the image URL. In the case when this
    is not possible, it generates a random UUID.

    There are two cases, the url follows one of the two following formats:
    1. https://ucampus.uchile.cl/d/r/usuario/2f/<uuid>/perfil/<img>.jpg
    2. https://ucampus.uchile.cl/d/images/siglas/<initials>.svg'
    """

    components = url.split("/")
    if components[4] == "r":
        return components[7]
    else:
        return uuid.uuid4()


def extract(html: str) -> dict[str, str]:
    soup = bs.BeautifulSoup(html, features="html.parser")
    ul = soup.find("ul", attrs={"class": "paginas"})
    li = ul.find("li", attrs={"class": "sel"})
    fecha_inicio_y_fin_semana = li.text
    inicio_semana, fin_semana = [
        f.strip() for f in fecha_inicio_y_fin_semana.split("al")
    ]
    first_day = datetime.strptime(inicio_semana, "%d/%m/%Y").date()
    table = soup.find("table", attrs={"class": "dhorario"})
    if table is None:
        return []
    tbody = table.find("tbody")
    tcols = tbody.find_all("td")
    data = []
    for i, col in enumerate(tcols):
        if i < 1 or i > 6:
            continue
        weekday = i
        day = first_day + timedelta(days=weekday - 1)
        rows = col.select("div.bloque")
        for r in rows:
            horario = r.find("h1").text
            cupos: str = r.find("h2").text

            participants = r.find("ul", attrs={"class": "participantes"})
            images = participants.select("img.photo.foto")
            image_sources = [i["src"] for i in images]
            user_ids = [get_user_uuid_from_image_url(src) for src in image_sources]

            start_time, end_time = [
                time.fromisoformat(s.strip()) for s in horario.split("-")
            ]
            duration = datetime.combine(day, end_time) - datetime.combine(
                day, start_time
            )
            capacity = int(cupos.split("/")[-1])

            data.append(
                {
                    "weekday": weekday,
                    "day": day,
                    "start_time": start_time,
                    "duration": duration,
                    "capacity": capacity,
                    "user_ids": user_ids,
                }
            )
    return data


def fetch_data():
    credentials = get_credentials()
    authenticated_session = login(
        user=credentials["user"], password=credentials["password"]
    )
    data: list[dict] = []
    today = date.today()
    for d in [today, today + timedelta(days=7)]:
        html = fetch(date=d, s=authenticated_session)
        data += extract(html)
    return data
