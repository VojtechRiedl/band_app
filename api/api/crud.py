from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import UploadFile
from datetime import datetime

from . import models
from .database import engine
from .schemas.ideas import IdeaCreate, Idea, IdeaUpdate, VoteCreate
from .schemas.plans import Plan, PlanCreate, PlanUpdate, PlanSuccessResponse
from .schemas.songs import Song, SongCreate, SongUpdate, FavoriteSongCreate
from .schemas.users import Authorization, AuthorizationFailed, User, UserUpdate

from . import files


def register(db: Session, authorization: Authorization):
    registered_user = db.query(models.Users).filter(models.Users.username == authorization.username).first()
    if registered_user:
        return AuthorizationFailed(
            username=authorization.username,
            error="Uživatel již existuje"
        )
    db_user = models.Users(
        username=authorization.username,
        password=authorization.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return User(
        id=db_user.user_id,
        username=db_user.username,
        created=db_user.created,
        last_login=db_user.last_login,
    )

def login(db: Session, authorization: Authorization):
    logged_user = db.query(models.Users).filter(models.Users.username == authorization.username, models.Users.password == authorization.password).first()
    if logged_user:
        db.query(models.Users).filter(models.Users.username == authorization.username).update({models.Users.last_login: func.now()})
        db.commit()
        db.refresh(logged_user)
        return User(
            id=logged_user.user_id,
            username=logged_user.username,
            created=logged_user.created,
            last_login=logged_user.last_login,
        )
    
    return AuthorizationFailed(
            username=authorization.username,
            error="Špatné jméno nebo heslo"
        )

def get_users(db: Session):
    users = db.query(models.Users).all()
    response_users = []
    if users:
        for user in users:
            response_users.append(User(
                id=user.user_id,
                username=user.username,
                created=user.created,
                last_login=user.last_login,
            ))
        return response_users
    return response_users
    
def get_user(db: Session, user_id: int):
    user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    if user:
        return User(
            id=user.user_id,
            username=user.username,
            created=user.created,
            last_login=user.last_login,
        )
    return None

def update_user(db: Session, user_id: int, user: UserUpdate):
    user = db.query(models.Users).filter(models.Users.username == user.username).first()
    
    if user is None:
        return None
    
    updated_user = db.query(models.Users).filter(models.Users.user_id == user_id).first()
    
    if updated_user is None:
        return None

    updated_user.username = user.username
    updated_user.password = user.password
    
    db.commit()
    db.refresh(updated_user)
    return User(
        id=updated_user.user_id,
        username=updated_user.username,
        created=updated_user.created,
        last_login=updated_user.last_login,
    )

def read_ideas(db: Session): 
    ideas = db.query(models.Ideas).all()
    
    if not ideas:
        return []
        
    return ideas

def read_idea(db: Session, idea_id: int):
    idea = db.query(models.Ideas).filter(models.Ideas.id == idea_id).first()
    if idea:
        return idea
    return None  
  
def create_idea(db: Session, idea_create: IdeaCreate):
    db_idea = models.Ideas(
        title=idea_create.title,
        description=idea_create.description,
        deadline=idea_create.deadline,
        user_id=idea_create.user_id
    )
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return idea_create

def create_vote(db: Session, vote_create: VoteCreate):
    vote = models.Votes(
        idea_id=vote_create.idea_id,
        user_id=vote_create.user_id,
        accepted=vote_create.like
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    
    return read_idea(db, vote.idea_id)

def read_vote(db: Session, idea_id: int, user_id: int):
    vote = db.query(models.Votes).filter(models.Votes.idea_id == idea_id, models.Votes.user_id == user_id).first()
    if vote:
        return vote
    return None

def delete_idea(db: Session, idea_id: int):    
    query = db.query(models.Ideas).filter(models.Ideas.id == idea_id)
    idea = query.first()
    
    if idea is None:
        return None

    
    query.delete()
    db.commit()
    return idea
    

def get_plans(db: Session):
    plans = db.query(models.Plans).all()
    response_plans = []
    if plans:
        for plan in plans:
            response_plans.append(Plan(
                plan_id=plan.plan_id,
                name=plan.name,
                plan_date=plan.date,
                description=plan.description,
                user=plan.users.username,
            ))
        return response_plans
    return response_plans

def get_plan(db: Session, plan_id: int):
    plan = db.query(models.Plans).filter(models.Plans.plan_id == plan_id).first()
    if plan:
        return Plan(
            plan_id=plan.plan_id,
            name=plan.name,
            plan_date=plan.date,
            description=plan.description,
            user=plan.users.username,
        )
    return None 

def create_plan(db: Session, idea_create: PlanCreate):
    db_plan = models.Plans(
        name=idea_create.name,
        date=idea_create.plan_date,
        description=idea_create.description,
        user_id=idea_create.user_id
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return idea_create

def update_plan(db: Session, plan_id: int, plan: PlanUpdate):
    updated_plan = db.query(models.Plans).filter(models.Plans.plan_id == plan_id).update({models.Plans.name: plan.name, models.Plans.date: plan.plan_date, models.Plans.description: plan.description})
    db.commit()
    return PlanSuccessResponse(
        plan_id=plan_id,
        rows_affacted=updated_plan,
        message="Nápad byl úspěšně aktualizován",
    ) 

def delete_plan(db: Session, plan_id: int):
    deleted_idea = db.query(models.Plans).filter(models.Plans.plan_id == plan_id).delete()
    db.commit()
    return PlanSuccessResponse(
        plan_id=plan_id,
        rows_affacted=deleted_idea,
        message="Nápad byl úspěšně smazán",
    )

def get_songs(db: Session):
    songs = db.query(models.Songs).all()
    response_songs = []
    if songs:
        for song in songs:
            response_songs.append(Song(
                song_id=song.song_id,
                name=song.name,
                video=song.video_path is not None,
                sound=song.song_path is not None,
                created=song.created,
                yt_link=song.yt_link,
                text=song.text,
                user=song.users.username,
            ))
        return response_songs
    return response_songs

def get_song(db: Session, song_id: int):
    song = db.query(models.Songs).filter(models.Songs.song_id == song_id).first()
    if song:
        return Song(
            song_id=song.song_id,
            name=song.name,
            video=song.video_path is not None,
            sound=song.song_path is not None,
            created=song.created,
            yt_link=song.yt_link,
            text=song.text,
            user=song.users.username,
        )
    return None

def get_favorite_songs(db: Session, user_id: int):
    songs = db.query(models.FavoriteSongs).join(models.Songs).filter(models.FavoriteSongs.user_id == user_id).all()
    
    favorite_songs = []
    
    if songs:
        for song in songs:
            favorite_songs.append(Song(
                song_id=song.songs.song_id,
                name=song.songs.name,
                video=song.songs.video_path is not None,
                sound=song.songs.song_path is not None,
                created=song.songs.created,
                yt_link=song.songs.yt_link,
                text=song.songs.text,
                user=song.songs.users.username,
            ))
        return favorite_songs
    return favorite_songs
    

def create_song(db: Session, song_create: SongCreate):
    song = models.Songs(
        name=song_create.name,
        yt_link=song_create.yt_link,
        text=song_create.text,
        user_id=song_create.user_id
    )
    db.add(song)
    db.commit()
    db.refresh(song)
    return Song(
        song_id=song.song_id,
        name=song.name,
        video=song.video_path is not None,
        sound=song.song_path is not None,
        created=song.created,
        yt_link=song.yt_link,
        text=song.text,
        user=song.users.username,
    )

def create_favorite_song(db: Session, favorire_song_create: FavoriteSongCreate):
    favorite_song = models.FavoriteSongs(
        song_id=favorire_song_create.song_id,
        user_id=favorire_song_create.user_id
    )
    db.add(favorite_song)
    db.commit()
    db.refresh(favorite_song)
    return Song(
        song_id=favorite_song.songs.song_id,
        name=favorite_song.songs.name,
        video=favorite_song.songs.video_path is not None,
        sound=favorite_song.songs.song_path is not None,
        created=favorite_song.songs.created,
        yt_link=favorite_song.songs.yt_link,
        text=favorite_song.songs.text,
        user=favorite_song.songs.users.username,
    )


def upload_sound(db: Session, song_id: int, sound_file : UploadFile):    
    query = db.query(models.Songs).filter(models.Songs.song_id == song_id)
    
    song = query.first()
    
    if song is None:
        return None
    
    path = files.save_sound_file("song_" + str(song.song_id), sound_file)
    
    query.update({models.Songs.song_path: path})
    db.commit()
    db.refresh(song)
    return Song(
        song_id=song.song_id,
        name=song.name,
        video=song.video_path is not None,
        sound=song.song_path is not None,
        created=song.created,
        yt_link=song.yt_link,
        text=song.text,
        user=song.users.username,
    )

def upload_video(db: Session, song_id: int, video_file : UploadFile):
    query = db.query(models.Songs).filter(models.Songs.song_id == song_id)
    
    song = query.first()
    
    if song is None:
        return None
    
    path = files.save_video_file("video_" + str(song.song_id), video_file)
    
    query.update({models.Songs.video_path: path})
    db.commit()
    db.refresh(song)
    
    return Song(
        song_id=song.song_id,
        name=song.name,
        video=song.video_path is not None,
        sound=song.song_path is not None,
        created=song.created,
        yt_link=song.yt_link,
        text=song.text,
        user=song.users.username,
    )

def get_video(db: Session, song_id: int):
    song = db.query(models.Songs).filter(models.Songs.song_id == song_id).first()
    if song is None:
        return None
    
    if song.video_path is None:
        return None
    
    return files.stream_video_file(song.video_path)

def get_sound(db: Session, song_id: int):
    song = db.query(models.Songs).filter(models.Songs.song_id == song_id).first()
    if song is None:
        return None
    
    if song.song_path is None:
        return None
    return files.stream_sound_file(song.song_path)

def update_song(db: Session, song_id: int, updated_song: SongUpdate):
    song = db.query(models.Songs).filter(models.Songs.song_id == song_id).first()
    if song is None:
        return None
    
    song.name = updated_song.name
    song.yt_link = updated_song.yt_link
    song.text = updated_song.text
    
    db.commit()
    db.refresh(song)
    return Song(
        song_id=song.song_id,
        name=song.name,
        video=song.video_path is not None,
        sound=song.song_path is not None,
        created=song.created,
        yt_link=song.yt_link,
        text=song.text,
        user=song.users.username,
    )

def delete_song(db: Session, song_id: int):
    query = db.query(models.Songs).filter(models.Songs.song_id == song_id)
    song = query.first()
    
    if song is None:
        return None
    
    deleted_song = Song(
        song_id=song.song_id,
        name=song.name,
        video=song.video_path is not None,
        sound=song.song_path is not None,
        created=song.created,
        yt_link=song.yt_link,
        text=song.text,
        user=song.users.username,
    )
    
    query.delete()
    db.commit()
    return deleted_song
    
