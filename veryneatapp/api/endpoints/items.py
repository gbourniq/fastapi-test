from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder

from typing import Dict, List, Optional, Union, Set
from veryneatapp.api.schemas.item import SimpleItem, CarItem, PlaneItem

router = APIRouter()


@router.get("/")
async def read_items():
    return [{"name": "Item Foo"}, {"name": "item Bar"}]


@router.get("/{item_id}")
async def read_item(item_id: str):
    return {"name": "Fake Specific Item", "item_id": item_id}


@router.put(
    "/{item_id}",
    tags=["custom"],
    responses={403: {"description": "Operation forbidden"}},
)
async def update_item(item_id: str):
    if item_id != "foo":
        raise HTTPException(
            status_code=403, detail="You can only update the item: foo"
        )
    return {"item_id": item_id, "name": "The Fighters"}


# Return list of models
@router.get("/response-list-of-models/", response_model=List[SimpleItem])
async def return_multiple_items():
    """
    Return list of items
    """
    # <data processing here>
    items = [
        {"name": "Foo", "description": "There comes my hero"},
        {"name": "Red", "description": "It's my aeroplane"},
    ]
    return items


# Return list of different models
items = {
    "item1": {"name": "Foow", "description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}


@router.get(
    "/get-item-or-404/{item_id}",
    response_model=Union[PlaneItem, CarItem],
    status_code=status.HTTP_200_OK,
)
async def read_item(item_id: str):
    """
    Must specify item1 or item2 to return model data, anything else returns a 404
    """
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Oooooops.. Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return items[item_id]


# Update car item with PUT (replace all object fields)
@router.put("/update/{item_id}", response_model=CarItem)
async def update_item(item_id: str, car_item: CarItem):
    """
    Must specify item1 representing the car item
    """
    update_item_encoded = car_item.dict()
    items[item_id] = update_item_encoded # updating car item in items dict
    return update_item_encoded


# Use PATCH to update specific fields (Partial updates)
# item.dict(exclude_unset=True) to generate a dict with only the data
# that was set (sent in the request), omitting default values
@router.patch("/partial-update/{item_id}", response_model=CarItem)
async def partial_update_item(item_id: str, item: CarItem):
    """
    Must specify item1 representing the car item
    """
    stored_item_data = items[item_id]
    stored_item_model = CarItem(**stored_item_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item

# Response with arbitrary dict
@router.get("/keyword-weights/", response_model=Dict[str, float])
async def read_keyword_weights():
    """
    returns arbitrary dict
    """
    return {"foo": 2.3, "bar": 3.4}
