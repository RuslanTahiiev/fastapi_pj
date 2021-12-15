from typing import Optional

from fastapi import FastAPI, Body, Cookie, status, Form, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic.fields import Field
from pydantic.networks import EmailStr

from utils import CommonQueryParams
from customexception import UnicornException
from models import Item, UserOut, UserIn, Offer, save_show_user
from queries import query_q, path_item_id
from data import items
from security import verify_token

# app = FastAPI(dependencies=[Depends(verify_token)])
app = FastAPI()

@app.get('/', status_code=status.HTTP_418_IM_A_TEAPOT)
def index():
    return {'Hello,': 'world!'}


@app.get('/items/{item_id}/name', response_model=Item, response_model_include=['name', 'description'])
async def read_item_name(commons = Depends(CommonQueryParams)):
    if commons.item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[commons.item_id]
    

@app.get('/items/{item_id}/public',  response_model=Item, response_model_exclude=['tax'])
async def read_item_public(commons = Depends(CommonQueryParams)):
    if commons.item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[commons.item_id]


@app.post('/items/', response_model=Item)
async def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    - **image**: some image
    """
    return item


@app.put('/items/{item_id}')
async def update_item(*, size: int = Body(...), user: Optional[UserIn] = None, item: Optional[Item] = None, commons = Depends(CommonQueryParams), q: Optional[str] = query_q):

    result = {'item_id': commons.item_id, 'size': size}
    
    if user:
        user_out: UserOut = save_show_user(user)
        result.update(user_out)
    
    item_dict = item.dict()    
    if item:
        if item.tax:
            price_with_tax = item.price + item.tax
            item_dict.update({'price_with_tax': price_with_tax})
        result.update({'item': item_dict})
        
    if q:
        result.update({'q': q})
    
    return result


@app.post('/offers/')
def create_offers(offer: Offer, q: Optional[str] = Cookie(None)):
    return offer


@app.post('/login/')
async def login(username: str = Form(...), email: EmailStr = Form(...), password: str = Form(...)):
    if password == 'password':
        raise UnicornException(name='Unicorn')
    return {'username': username}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}


@app.patch("/items/{item_id}", response_model=Item)
async def update_item(item: Item, commons = Depends(CommonQueryParams)):
    stored_item_data = items[commons.item_id]
    stored_item_model = Item(**stored_item_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    items[commons.item_id] = jsonable_encoder(updated_item)
    return updated_item


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )
    