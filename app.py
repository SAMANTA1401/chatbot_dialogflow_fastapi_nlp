from typing import Union
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import db_helper
import generic_helper

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    session_id = generic_helper.extract_session_id(output_contexts[0]['name'])


    intent_handeler_dict = {
        'order.add - context:ongoing-order': add_to_order,
        'order.remove-context:ongoing-order' :remove_from_order,
        'order.complete-context:ongoing-order': complete_order,
        'track.order-context:ongoing-tracking' : track_order,

    }

    return intent_handeler_dict[intent](parameters, session_id)

    
inprogress_orders = {}
def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-items"]
    quantites = parameters["number"]
    
    if len(food_items) != len(quantites):
        fullfillment_text = "sorry I din't understand , Can you please specify food items and quantities."
    else:
        new_food_dict = dict(zip(food_items, quantites))

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict

        else:
            inprogress_orders[session_id] = new_food_dict

        print(inprogress_orders)
    
        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fullfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={
            "fulfillmentText": fullfillment_text
        })
        
        
    
def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfilment_text = "I am having a trouble to find your order . Sorry ! Can you place a new order."
    else:
        # order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        # fulfilment_text = f"Your order of {order_str} is confirmed. It will be delivered in 30 mins. Thankyou!"
        order = inprogress_orders[session_id]
        order_id = db_helper.save_to_db(order)

        if order_id == -1:
            fulfilment_text = "I am having a trouble to place your order . Sorry ! Can you place a new order."

        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfilment_text = f"Awesome. We have placed your order. Here is your order id {order_id}. your "\
                               f"order of Rs- {order_total}/- will be delivered in 30 mins. Thankyou!"
            
        del inprogress_orders[session_id]

    return JSONResponse(
        content={
            "fulfillmentText": fulfilment_text
        }
    )

def track_order(parameters: dict, session_id: str):
    order_id =int(parameters.get('order_id'))
    # customer_id = parameters.get('customer_id')
    print(order_id)
    order_status = db_helper.get_order_status(order_id)
    if order_status:
        fullfillment_text = f"The order status for order id: {order_id} is : {order_status}"
    else:
        fullfillment_text = f"No order found for order id: {order_id}"

    return JSONResponse(content={
            "fulfillmentText": fullfillment_text
        })

def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fullfillment_text = "I am having a trouble to find your order . Sorry ! Can you place a new order."
        return JSONResponse(content={
            "fulfillmentText": fullfillment_text
        })
    current_order = inprogress_orders[session_id]
    food_items = parameters.get('food-items')

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        removed_items_str = ", ".join(removed_items)
        fullfillment_text = f"Removed {removed_items_str} from your order."
    if len(no_such_items) > 0:
        no_such_items_str = ", ".join(no_such_items)
        fullfillment_text += f"Sorry, there is no {no_such_items_str} in your order."
    if len(current_order.keys()) == 0:
        fullfillment_text +="your order is empty"
    
    order_str = generic_helper.get_str_from_food_dict(current_order)
    fullfillment_text += f"Your current order is: {order_str}"

    print(inprogress_orders)

    return JSONResponse(content={
        "fulfillmentText": fullfillment_text
    })