import datetime
from typing import List, Union

from fastapi import FastAPI, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from .db import models, crud, schemas
from .db.init import SessionLocal, engine
from .utils import get_real_which_day

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.get('/', response_model=schemas.StatusRetSucc)
# async def root(db: Session = Depends(get_db)):
#     crud_res = crud.get_status(db)
#     return schemas.StatusRetSucc(status=crud_res)


@app.get('/status', response_model=schemas.StatusRet)
async def status_get(db: Session = Depends(get_db)):
    return schemas.StatusRet(**crud.status.get(db))


@app.get('/battle/log', response_model=List[schemas.BattleLog])
async def battle_log_get(who: int = None, which_day: Union[datetime.date, str] = None, db=Depends(get_db)):
    return crud.battle_log.get(db, who=who, which_day=get_real_which_day(which_day))


@app.post('/battle/log', response_model=schemas.BattleLogRet)
async def battle_log_post(commit: schemas.BattleLogCommit, db=Depends(get_db)):
    status, ret = crud.battle_log.commit(db, commit)
    if not status:
        raise HTTPException(403, jsonable_encoder(ret))
    return ret


@app.get('/battle/log/count', response_model=int)
async def battle_log_count(who: str = None, which_day: Union[datetime.date, str] = None, db=Depends(get_db)):
    return crud.battle_log.count(db, who=who, which_day=get_real_which_day(which_day))


@app.get('/battle/current', response_model=List[schemas.CurrentBattle])
async def battle_current_get(who: str = None, which_boss: int = None, type: models.CurrentBattle.Types = None,
                             db=Depends(get_db)):
    return crud.current_battle.get(db, who, which_boss, [type == models.CurrentBattle.type] if type else ())


@app.post('/battle/current', response_model=schemas.CurrentBattleRet)
async def battle_current_post(commit: schemas.CurrentBattleCommit, db=Depends(get_db)):
    status, ret = crud.current_battle.commit(db, commit)
    if not status:
        raise HTTPException(403, jsonable_encoder(ret))
    return ret


@app.get('/member', response_model=List[schemas.Member])
async def member_get(game_id: int = None, contact_khl: str = None, contact_qq: str = None, db=Depends(get_db)):
    return crud.member.get(db, game_id=game_id, contact_khl=contact_khl, contact_qq=contact_qq)


@app.post('/member', response_model=schemas.Member)
async def member_post(member: schemas.MemberAdd, db=Depends(get_db)):
    status, ret = crud.member.add(db, member)
    if not status:
        raise HTTPException(403, jsonable_encoder(ret))
    return ret
