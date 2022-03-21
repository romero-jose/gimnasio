from datetime import date
import requests
import bs4 as bs

# from bs4 import soup

URL = "https://ucampus.uchile.cl/m/fcfm_reservas/detalle"
# id=70&fecha=2022-03-21


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


def fetch(date: date) -> str:
    cookies = {
        "_ga": "GA1.2.391761329.1614555898",
        "_LB": "ucampus81-int",
        "_fcfm": "2kic1hge4vrs1d6235t79mia3r",
        "SESSID_upasaporte": "7v3hpscd38ff1i3e7ugksmee9p",
        "res": "1920",
        "io": "ga3mZIor5Qdr1Gio4YJ0",
        "username": "joseromero",
    }
    response = requests.get(
        URL, params={"id": 70, "fecha": date.isoformat()}, cookies=cookies
    )
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


def print(data):
    for d in data:
        print(f"|=========================================|")
        print(f"| Dia:     {weekday(d['dia'])}")
        print(f"| Horario: {d['horario']}")
        print(f"| Cupos:   {d['cupos']}")
        print(f"| Enlace:  {d['enlace']}")

def main():
    html = fetch(date.today())
    data = extract(html)
    print(data)


if __name__ == "__main__":
    main()
