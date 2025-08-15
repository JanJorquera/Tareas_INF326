from enum import Enum

import logging
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId

from fastapi import FastAPI, Query
from pydantic import BaseModel


app = FastAPI()
mongodb_client = MongoClient("service_02_mongodb", 27017)

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


class Country(str, Enum):
    chile = 'Chile'
    portugal = 'Portugal'
    españa = 'España'
    francia = "Francia"


class Team(BaseModel):
    id: str | None = None
    name: str
    country: Country

    description: str = ""

    def __init__(self, **kargs):
        if "_id" in kargs:
            kargs["id"] = str(kargs["_id"])
        BaseModel.__init__(self, **kargs)


@app.get("/")
async def root():
    logging.info("👋 Hello world (end-point)!")
    return {"Hello": "World"}


def get_players_of_a_team(team_id) -> list[Player]:
    url = f"http://service_01:80/players?team_id={team_id}"
    logging.info(f"🌍 Request [GET] {url}")

    response = requests.get(url)

    if response.status_code != 200:
        logging.warning(f"Team with id {team_id} not found or error from service_02 (status {response.status_code})")
        raise HTTPException(status_code=500, detail="Error fetching players from service_01")

    try:
        return response.json()
    except ValueError:
        logging.error(f"Invalid JSON response when fetching players of team_id: {team_id}")
        return None

@app.get("/teams")
def teams_all(expand: list[str] = Query(default=[])):
    teams = [Team(**team).dict()
             for team in mongodb_client.service_02.teams.find({})]

    # n+1 problem...
    if expand and 'players' in expand:
        logging.warning("🚨 n+1 requests...")
        for i, team in enumerate(teams):
            logging.info(f"Trying to establish communication with service_01")
            teams[i]["players"] = get_players_of_a_team(team['id'])
            logging.info(f'Players of team (team_id: {team["id"]}): {teams[i]["players"]}')

    return teams


@app.get("/teams/{team_id}")
def teams_get(team_id: str, expand: list[str] = Query(default=[])):
    doc = mongodb_client.service_02.teams.find_one({"_id": ObjectId(team_id)})
    if doc is None:
        logging.warning(f"No team found with id {team_id}")
        return {"error": "Team not found"}, 404

    team = Team(**doc).dict()

    logging.info(f"Getting all players of team_id: {team_id})")
    if expand and 'players' in expand:
        logging.info(f"Trying to establish communication with service_01")
        team["players"] = get_players_of_a_team(team_id)
        logging.info(f'Players of team (team_id: {team_id}): {team["players"]}')

    return team


@app.delete("/teams/{team_id}")
def teams_delete(team_id: str):
    mongodb_client.service_02.teams.delete_one({"_id": ObjectId(team_id)})
    logging.info(f"Deleted team with id {team_id}")
    return {"status": "ok"}


@app.post("/teams")
def teams_create(team: Team):
    inserted_id = mongodb_client.service_02.teams.insert_one(
        team.dict()
    ).inserted_id

    new_team = Team(
        **mongodb_client.service_02.teams.find_one(
            {"_id": ObjectId(inserted_id)}
        )
    )

    logging.info(f"✨ New team created: {new_team}")

    return new_team

@app.put("/teams/{team_id}")
def teams_update(team_id: str, team: Team):
    update_data = team.dict()
    update_data.pop("_id", None)
    update_data.pop("id", None)

    updated_team_data = mongodb_client.service_02.teams.find_one_and_update(
        {"_id": ObjectId(team_id)},
        {"$set": update_data},
        return_document=True
    )

    if updated_team_data:
        new_team = Team(**updated_team_data)
        logging.info(f"Team updated: {new_team}")
        return new_team
    else:
        logging.warning(f"No team found with id {team_id}")
        return "operation not performed"

@app.get("/teams/{team_id}/avg-age")
def average_age(team_id: str):

    players = get_players_of_a_team(team_id)

    if players:
        total_age = sum(player["age"] for player in players)
        avg_age = total_age / len(players)

        logging.info(f"Average age for team_id={team_id} is {avg_age:.2f}")
        return {"avgAge": avg_age}

    logging.warning(f"No team found with id {team_id}")
    return {"avgAge": -1}

@app.get("/teams/{team_id}/total-injured")
def total_injured(team_id: str):
    players = get_players_of_a_team(team_id)

    if players:
        total_injured = sum(1 for player in players if player["injured"])

        logging.info(f"Total injureds for team_id={team_id} is {total_injured}")
        return {"total_injured": total_injured}

    logging.warning(f"No team found with id {team_id}")
    return {"total_injured": -1}