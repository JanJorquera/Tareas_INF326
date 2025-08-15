

import logging
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId

from fastapi import FastAPI, Query
from pydantic import BaseModel


app = FastAPI()
mongodb_client = MongoClient("service_01_mongodb", 27017)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s;%(levelname)s;%(name)s;%(message)s'
)

class Player(BaseModel):
    id: str | None = None
    name: str
    age: int
    number: int
    team_id: str | None = None
    description: str = ""
    injured: bool | None = False

    def __init__(self, **kargs):
        if "_id" in kargs:
            kargs["id"] = str(kargs["_id"])
        BaseModel.__init__(self, **kargs)


@app.get("/")
async def root():
    logging.info("👋 Hello world (end-point)!")
    return {"Hello": "World"}
    
def get_team(team_id):
    url = f"http://service_02:80/teams/{team_id}"
    logging.info(f"🌍 Request [GET] {url}")

    response = requests.get(url)
    if response.status_code != 200:
        logging.warning(f"Team with id {team_id} not found or error from service_02 (status {response.status_code})")
        return None
    
    try:
        return response.json()
    except ValueError:
        logging.error(f"Invalid JSON response when fetching team {team_id}")
        return None

@app.get("/players",
         response_model=list[Player])
def players_all(team_id: str | None = None):
    """Prueba"""
    logging.info(f"Getting all players (team_id: {team_id})")
    filters = {}

    if team_id:
        filters["team_id"] = team_id

    return [Player(**player) for player in mongodb_client.service_01.players.find(filters)]


@app.get("/players/{player_id}")
def players_get(player_id: str):
    doc = mongodb_client.service_01.teams.find_one({"_id": ObjectId(player_id)})
    if doc is None:
        logging.warning(f"No player found with id {player_id}")
        return {"error": "Team not found"}, 404

    player = Player(**doc).dict()
    logging.info(f"Getting player with id {player_id}: {player}")
    return player


@app.delete("/players/{player_id}")
def players_delete(player_id: str):
    mongodb_client.service_01.players.delete_one(
        {"_id": ObjectId(player_id)}
    )
    logging.info(f"Deleted player with id {player_id}")
    return "ok"


@app.post("/players")
def players_create(player: Player):
    inserted_id = mongodb_client.service_01.players.insert_one(
        player.dict()
    ).inserted_id

    new_player = Player(
        **mongodb_client.service_01.players.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    )

    logging.info(f"✨ New player created: {new_player}")

    return new_player

@app.put("/players/{player_id}")
def players_update(player_id: str, player: Player):
    update_data = player.dict()
    update_data.pop("_id", None)
    update_data.pop("id", None)
    
    updated_player_data = mongodb_client.service_01.players.find_one_and_update(
        {"_id": ObjectId(player_id)},
        {"$set": update_data},
        return_document=True
    )

    if updated_player_data:
        new_player = Player(**updated_player_data)
        logging.info(f"Player updated: {new_player}")
        return new_player
    else:
        logging.warning(f"No player found with id {player_id}")
        return "operation not performed"

@app.patch("/players/{player_id}/injured")
def mark_injured(player_id: str):
    player = mongodb_client.service_01.players.find_one({"_id": ObjectId(player_id)})

    if player:
        updated_player_data = mongodb_client.service_01.players.find_one_and_update(
            {"_id": ObjectId(player_id)},
            {"$set": {"injured": not player.get("injured", False)}},
            return_document=True
        )

        new_player = Player(**updated_player_data)
        logging.info(f"Player updated: {new_player}")
        return new_player
    else:
        logging.warning(f"No player found with id {player_id}")
        return "operation not performed"

@app.patch("/players/{player_id}")
def transfer_player(player_id: str, team_id: str | None = Query(default=None)):
    player = mongodb_client.service_01.players.find_one({"_id": ObjectId(player_id)})

    if team_id:
        team = get_team(team_id)
        
        if not team:
            return "operation not performed"
            
    if player:
        updated_player_data = mongodb_client.service_01.players.find_one_and_update(
            {"_id": ObjectId(player_id)},
            {"$set": {"team_id": team_id}},
            return_document=True
        )

        new_player = Player(**updated_player_data)
        logging.info(f"Player updated: {new_player}")
        return new_player
    else:
        logging.warning(f"No player found with id {player_id}")
        return "operation not performed"
