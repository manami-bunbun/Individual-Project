import logging
import os
import secrets
from fastapi import FastAPI, HTTPException, Request, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse
from datetime import datetime
from google.oauth2.credentials import Credentials
import google_auth_oauthlib.flow
import json
import random
import uvicorn
import getEmail
import data
from config import CLIENT_ID, CLIENT_SECRET
from typing import Dict, List
import httpx
from pydantic import BaseModel

class UpdateRowsRequest(BaseModel):
    condition: str
    selected_rows: dict 

logging.basicConfig(level=logging.INFO)

os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # すべてのオリジンを許可
#     allow_credentials=True,
#     allow_methods=["*"],  # すべてのHTTPメソッドを許可
#     allow_headers=["*"],  # すべてのヘッダーを許可
# )

app.add_middleware(SessionMiddleware, secret_key="INDIVIDUALPROJECT", max_age=3600)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# global variable
mail_data=[]
random_conditions = ["All", "Sender", "Date", "Title", "Body"]
random.shuffle(random_conditions)
viewed_mails = []
selected_rows = []


CLIENT_SECRETS_FILE = "client_secret.json"
REDIRECT_URI = 'https://redirectmeto.com/http://127.0.0.1:8000/auth'
# REDIRECT_URI = 'http://127.0.0.1:8000/auth'
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]


# Page
@app.get("/")
def index(request: Request):
    userID = request.session.get('userID')
    if not userID:
        return RedirectResponse('/login', status_code= 302)

    return RedirectResponse('/home')

@app.get("/home")
def home(request: Request):
    userID = request.session.get('userID')
    if not userID:
        return RedirectResponse('/login')
    
    logging.info('numbers, -----------------user: %s-----------------------' % userID)
    
    # current_step = request.session.get('current_step', 1)

    return templates.TemplateResponse(
        name="home.html",
        context={"request": request}
    )

@app.get('/welcome')
def welcome(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(
        name='welcome.html',
        context={'request': request}
    )

@app.get("/login")
async def login(request: Request, response: Response):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = request.url_for('auth')


    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    request.session['state'] = state
    response.set_cookie(key=state, value=state, httponly=True)
    return RedirectResponse(authorization_url)

@app.route('/auth')
async def auth(request: Request):
    state = request.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = request.url_for('auth')


    authorization_response = str(request.url)

    flow.fetch_token(authorization_response=authorization_response)
    print('fetch_token:', authorization_response)

    credentials = flow.credentials
    print('credentials:', credentials)
    request.session['credentials'] = await credentials_to_dict(credentials)

    random_conditions = ["All", "Sender", "Date", "Title", "Body"]
    random.shuffle(random_conditions)
    request.session['random_conditions'] = random_conditions

    return RedirectResponse('/create_record')

@app.route('/create_record')
async def create_record(request: Request):

    credentials = request.session['credentials']

    mail_data, emailaddress = getEmail.get_email_data(credentials)
    mail_data_dict = [email.to_dict() for email in mail_data]

    userID = emailaddress.split('@')[0]
    request.session['userID']=userID

    file_path = f"record/real-email/{userID}.json"
    if os.path.exists(file_path):
        os.remove(file_path)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(mail_data_dict, file, ensure_ascii=False, indent=4)

    return RedirectResponse('/home')


@app.get('/logout')
async def logout(request: Request):
    response = RedirectResponse('/login', status_code= 302)
    state = request.session.get('state')
    response.delete_cookie(state)

    request.session.clear()
    return HTMLResponse(content='you successfully logged out! This is the end of experiment.\n Thank you so much for participating!\n\n')
    

@app.get('/privacy-policy')
def privacy_policy(request: Request):
    return templates.TemplateResponse(
        name='privacy-policy.html',
        context={'request': request}
    )

# 条件適用ページ
@app.get("/experiments/{condition}")
async def experiments(request: Request, condition: str):
    userID = request.session.get('userID')
    mail_data=get_record(userID)
    experiment_data = data.get_condition_data(mail_data, condition)
    return templates.TemplateResponse("gmail.html", {"request": request, "condition": condition, "experiment_data": experiment_data})


@app.post("/experiments/{condition}")
async def experiments(request: Request, condition: str):
    userID = request.session.get('userID')
    mail_data=get_record(userID)
    experiment_data = data.get_condition_data(mail_data, condition)
    return templates.TemplateResponse("gmail.html", {"request": request, "condition": condition, "experiment_data": experiment_data})


class QuestionnaireForm(BaseModel):
    mental_demand: str
    physical_demand: str
    pace: str
    success: str
    hard_work: str
    emotions: str
    info_infer: str
    inbox_info_high: str
    inbox_info_low: str

async def save_form_data(user_id: str, condition: str, form_data: QuestionnaireForm):
    form_dict = form_data.dict()

    file_path = f"./record/form/{user_id}.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        data = []

    entry = {"condition": condition, "form_data": form_dict}

    data.append(entry)

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    return

@app.get("/questionnaire/{condition}", response_class=HTMLResponse)
async def show_questionnaire(request: Request, condition: str):
    return templates.TemplateResponse("questionnaire.html", {"request": request, "condition": condition})

@app.post("/questionnaire/{condition}")
async def process_questionnaire(request: Request, condition: str, form_data: QuestionnaireForm):
    user_id = request.session.get("userID")
    # data = await request.json()
    # return {"message": "data={}".format(data)}
    # form_data = data.get("form_data")
    logging.info("form_data={}".format(form_data))
    # condition = data.get("condition")
    if not user_id:
        return {"error": "User ID not found in session"}

    await save_form_data(user_id, condition, form_data)
    return {"message": "Form data saved successfully."}




@app.get("/end")
def end_page(request: Request):
    # timestamp = datetime.now().strftime("%m-%d_%H-%M-%S")
    # mail_data_serializable = [email.__dict__ for email in mail_data]
    # mail_data_json = json.dumps(mail_data_serializable, indent=4, ensure_ascii=False)
    # file_path = f"record/json/{timestamp}.json"
    # with open(file_path, "w", encoding="utf-8") as file:
    #     file.write(mail_data_json)
    return RedirectResponse("/logout")


# API

# 開始ボタンがクリックされたとき
@app.get("/start")
async def start_experiment():
    # 最初の条件の適用ページにリダイレクト
    return RedirectResponse("/apply-random-condition")

class UpdateSelectedRowsRequest(BaseModel):
    condition: str
    selected_rows: Dict[str, int]


@app.post("/update-selected-rows")
async def update_selected_rows(request: Request):
    data = await request.json()
    userID = request.session.get('userID')
    mail_data=get_record(userID)

    condition = data.get('condition') 
    # recordTime = data.get('recordTime') 
    selected_rows = data.get('selectedRows')

    logging.info("selectedRows={}".format(selected_rows))

    # return {"message": "mail_data: %s" % mail_data}

    try:
        for original_index, selection_order in selected_rows.items():
            original_index_str = str(original_index)            
            for mail in mail_data:
                if str(mail.original_index) == original_index_str:
                    mail.numbers[condition] = int(selection_order)
                    logging.info(f"numbers, condition: {condition}, original_index: {original_index_str}, selection_order:{mail.numbers[condition]}")
                    break
            
        await update_record(userID, mail_data)
        # update_time_record(userID, condition, recordTime)
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"message": "Row Order updated successfully."}

# ランダムな条件の設定
@app.route("/apply-random-condition", methods=["GET", "POST"])
async def apply_random_condition(request: Request):
    random_conditions = request.session.get('random_conditions')

    if not random_conditions:
        return Response(status_code=307, headers={"Location": "/home"})
    random_condition = random_conditions.pop()
    request.session['random_conditions'] = random_conditions
    return RedirectResponse(url=f"/experiments/{random_condition}")

@app.get("/step/{step_number}")
async def update_step(step_number: int, request: Request):
    request.session['current_step'] = step_number + 1
    return RedirectResponse(url="/home", status_code=302)



# helpers
@app.post("/update-time-record")
async def update_time_record(request: Request):
    user_id = request.session.get('userID')
    
    data = await request.json()
    condition = data['condition']
    recordTime = data['recordTime']

    file_path = f"record/time/{user_id}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            time_data = json.load(file)
    else:
        time_data = {}

    time_data[condition] = recordTime

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(time_data, file, indent=4)
    
    return

async def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


async def dict_to_credentials(cred_dict):

    return Credentials(
        token=cred_dict.get("token"),
        refresh_token=cred_dict.get("refresh_token"),
        token_uri=cred_dict.get("token_uri"),
        client_id=cred_dict.get("client_id"),
        client_secret=cred_dict.get("client_secret"),
        scopes=cred_dict.get("scopes")
    )


def get_record(user_id: str):
    file_path = f"record/real-email/{user_id}.json"
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                mail_data = json.load(file)
            return [getEmail.Email.from_dict(email) for email in mail_data]
    except Exception as e:
        logging.error(f"Error getting record for : {e}")
    return

async def update_record(user_id, mail_data):
    file_path = f"record/real-email/{user_id}.json"
    try:
        mail_data_dict = [email.to_dict() for email in mail_data]
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(mail_data_dict, file, ensure_ascii=False, indent=4)
        
    except Exception as e:
        logging.error(f"Error updating number record for : {e}")
    
    return



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
