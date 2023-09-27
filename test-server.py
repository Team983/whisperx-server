from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Union
from starlette.responses import JSONResponse

app = FastAPI()

class CompleteRequest(BaseModel):
    noteId: str
    result: Union[dict, str]

class ErrorRequest(BaseModel):
    noteId: str
    message: str

complete_request_dict = dict()
error_request_dict = dict()

total_completed = 0
total_error = 0

@app.post("/asr-completed/{note_id}")
async def PostCompleteRequest(note_id:str, request:CompleteRequest):
    global complete_request_dict
    global total_completed
    request_dict = dict(request)
    request_dict['success'] = True
    complete_request_dict[note_id] = request_dict
    total_completed += 1
    return JSONResponse(request_dict)


@app.post("/asr-error/{note_id}")
async def PostErrorRequest(note_id:str, request:ErrorRequest):
    global error_request_dict
    global total_error
    request_dict = dict(request)
    request_dict['success'] = True
    error_request_dict[note_id] = request_dict
    total_error += 1
    return JSONResponse(request_dict)


@app.get('/asr-completed/{note_id}')
async def GetCompleteRequest(note_id:str):
    try:
        return JSONResponse(complete_request_dict[note_id])
    except:
        return JSONResponse({"success": False})


@app.get('/asr-error/{note_id}')
async def GetErrorRequest(note_id:str):
    try:
        return JSONResponse(error_request_dict[note_id])
    except:
        return JSONResponse({"success": False})


@app.get('/number_completed')
async def GetNumberCompleted():
    return JSONResponse({"number_completed": total_completed})


@app.get('/number_error')
async def GetNumberError():
    return JSONResponse({"number_error": total_error})


