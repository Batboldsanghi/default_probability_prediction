
from fastapi import FastAPI, Security,  HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt, json;
from models import requests
from passlib.context import CryptContext
from datetime import datetime, timedelta
import config

from pandas import DataFrame,read_json
import json
from joblib import load
from utils import data_clean_production
from numpy import mean

security = HTTPBearer()
app = FastAPI()
catb_models = [load("files/catboost_notbalanced_{0}.pkl".format(i)) for i in range(10)]
scaler = load("files/scaler_mm.pkl")

users =[
    {
        "username":"", 
        "password":""
    },
    {
        "username":"", 
        "password":"" 
    }
]

hasher = CryptContext(schemes=['bcrypt'])


def encode_token(username):
        payload = {
            'exp' : datetime.utcnow() + timedelta(days=0, minutes=30),
            'iat' : datetime.utcnow(),  
            'scope': 'access_token',          
            'sub' : username
        }
        
        return jwt.encode(
            payload, 
            config.JWT_CONFIG['secret'],
            algorithm=config.JWT_CONFIG['algorithms']
        )

def decode_token(token):
    try:
        payload = jwt.decode(token, config.JWT_CONFIG['secret'], algorithms=['HS256'])        
        if (payload['scope'] == 'access_token'):
            return payload['sub']   
        raise HTTPException(status_code=401, detail='Scope for the token is invalid')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

#-------------------------------------------
@app.get("/")
async def root():
    return {"message": "Hello Klarna"}


@app.post("/auth/token")
async def authToken(auth: requests.Auth):
    
    user = next((user for user in users if user["username"]==auth.username),None)
    if(user==None):
        raise HTTPException(401,"invalid username and password")
    if(not (auth.username == user["username"] and hasher.verify(auth.password,user["password"]))):
        raise HTTPException(401,"invalid username and password")

    access_token = encode_token(auth.username)

    return {
        "result":"OK",
        'access_token':access_token
    }

# async def req1(data: requests.Req1, credentials: HTTPAuthorizationCredentials = Security(security)):    
#     decode_token(credentials.credentials)

@app.post("/req1")
async def req1(data: requests.Req1, credentials: HTTPAuthorizationCredentials = Security(security)):    
    decode_token(credentials.credentials)

    data_dict = data.dict(exclude={'uuid'})
    print(data_dict)
    df_request = DataFrame.from_dict(data_dict,orient="index").T
    df_request = data_clean_production(df_request)

    X = scaler.transform(df_request)

    y_pred_catboost = [catb_models[i].predict_proba(X)[:, 1] for i in range(10)]
    y_pred_catboost_mean= mean(y_pred_catboost)

    return {
        "result":"OK",
        "uuid":data.uuid,
        "pd":round(y_pred_catboost_mean,6)
    }
