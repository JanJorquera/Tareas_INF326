import requests
import time

BASE_URL_TEAMS = "http://service_02:80"
BASE_URL_PLAYERS = "http://service_01:80"

# Crear equipos (teams)
teams_data = [
    {
        "name": "Colo-Colo",
        "country": "Chile",
        "description": "Equipo más popular de Chile"
    },
    {
        "name": "Sporting CP",
        "country": "Portugal",
        "description": "Academia de cracks como Cristiano Ronaldo"
    },
    {
        "name": "FC Barcelona",
        "country": "España",
        "description": "Cuna del tiki-taka"
    },
    {
        "name": "Paris Saint-Germain",
        "country": "Francia",
        "description": "Dominio en la Ligue 1"
    }
]

team_ids = []
for team in teams_data:
    r = requests.post(f"{BASE_URL_TEAMS}/teams", json=team)
    if r.status_code == 200:
        team_created = r.json()
        print(f"✅ Equipo creado: {team_created}")
        team_ids.append(team_created["id"])
    else:
        print(f"❌ Error creando equipo: {r.text}")
    time.sleep(5)

# Crear jugadores (players) con los team_ids recién creados
players_data = [
    {
        "name": "Lionel Messi",
        "age": 37,
        "number": 10,
        "team_id": team_ids[0] if len(team_ids) > 0 else None,
        "description": "GOAT argentino",
        "injured": False
    },
    {
        "name": "Cristiano Ronaldo",
        "age": 40,
        "number": 7,
        "team_id": team_ids[1] if len(team_ids) > 1 else None,
        "description": "Leyenda portuguesa",
        "injured": False
    },
    {
        "name": "Kylian Mbappé",
        "age": 26,
        "number": 7,
        "team_id": team_ids[2] if len(team_ids) > 2 else None,
        "description": "Velocista francés",
        "injured": True
    }
]

player_ids = []
for player in players_data:
    if player["team_id"] is None:
        print(f"❌ No se pudo asignar team_id para jugador {player['name']} porque no hay suficientes equipos creados.")
        continue
    r = requests.post(f"{BASE_URL_PLAYERS}/players", json=player)
    if r.status_code == 200:
        player_created = r.json()
        print(f"✅ Jugador creado: {player_created}")
        player_ids.append(player_created["id"])
    else:
        print(f"❌ Error creando jugador: {r.text}")
    time.sleep(5)

# Listar jugadores
r = requests.get(f"{BASE_URL_PLAYERS}/players")
print("📋 Lista de jugadores:", r.json())
time.sleep(5)

# Actualizar jugador
if player_ids:
    update_data = {
        "name": "Lionel Andrés Messi",
        "age": 38,
        "number": 30,
        "team_id": team_ids[0],
        "description": "GOAT argentino actualizado",
        "injured": False
    }
    r = requests.put(f"{BASE_URL_PLAYERS}/players/{player_ids[0]}", json=update_data)
    print("✏ Jugador actualizado:", r.json())
    time.sleep(5)

# Marcar jugador como lesionado (toggle)
if len(player_ids) > 1:
    r = requests.patch(f"{BASE_URL_PLAYERS}/players/{player_ids[1]}/injured")
    print("🤕 Jugador lesionado:", r.json())
    time.sleep(5)

# Transferir jugador
if len(player_ids) > 2 and len(team_ids) > 3:
    nuevo_team_id = team_ids[3]  # último equipo creado
    r = requests.patch(f"{BASE_URL_PLAYERS}/players/{player_ids[2]}?team_id={nuevo_team_id}")
    print("🔄 Jugador transferido:", r.json())
    time.sleep(5)

# Eliminar jugador
if len(player_ids) > 1:
    r = requests.delete(f"{BASE_URL_PLAYERS}/players/{player_ids[1]}")
    print("🗑 Jugador eliminado:", r.text)
    time.sleep(5)

# Listar equipos
r = requests.get(f"{BASE_URL_TEAMS}/teams")
print("📋 Lista de equipos:", r.json())
time.sleep(5)

# Obtener equipo con jugadores (expand=players)
if team_ids:
    r = requests.get(f"{BASE_URL_TEAMS}/teams/{team_ids[0]}?expand=players")
    print(f"👥 Equipo con jugadores: {r.json()}")
    time.sleep(5)

# Actualizar equipo
if team_ids:
    update_team_data = {
        "name": "Colo-Colo Actualizado",
        "country": "Chile",
        "description": "El eterno campeón chileno"
    }
    r = requests.put(f"{BASE_URL_TEAMS}/teams/{team_ids[0]}", json=update_team_data)
    print("✏ Equipo actualizado:", r.json())
    time.sleep(5)

# Consultar edad promedio del equipo
if team_ids:
    r = requests.get(f"{BASE_URL_TEAMS}/teams/{team_ids[0]}/avg-age")
    print("📊 Edad promedio:", r.json())
    time.sleep(5)

# Consultar lesionados totales del equipo
if team_ids:
    r = requests.get(f"{BASE_URL_TEAMS}/teams/{team_ids[0]}/total-injured")
    print("🤕 Lesionados totales:", r.json())
    time.sleep(5)

# Eliminar equipo
if len(team_ids) > 1:
    r = requests.delete(f"{BASE_URL_TEAMS}/teams/{team_ids[1]}")
    print("🗑 Equipo eliminado:", r.text)
    time.sleep(5)