
import mysql.connector
global cnx

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ShubhaYes@1401",
    database="pandeyji_eatery"
)

# Function to fetch the order status from the order_tracking table
def get_order_status(order_id):
    cursor = cnx.cursor()

    # Executing the SQL query to fetch the order status
    query = f"SELECT status FROM order_tracking WHERE order_id = {order_id};"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()

    # Closing the cursor
    cursor.close()

    # Returning the order status
    if result:
        return result[0]
    else:
        return None


def get_next_order_id():
    cursor = cnx.cursor()

    # Executing the SQL query to fetch the next order ID
    query = "SELECT MAX(order_id) FROM orders;"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    # Returning the next order ID
    if result:
        return result + 1
    else:
        return 1
    

# Function to call the MySQL stored procedure and insert an order item
def insert_order_item(food_item, quantity, order_id):
    try:
        cursor = cnx.cursor()

        # Calling the stored procedure
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))

        # Committing the changes
        cnx.commit()

        # Closing the cursor
        cursor.close()

        print("Order item inserted successfully!")

        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")

        # Rollback changes if necessary
        cnx.rollback()

        return -1

    except Exception as e:
        print(f"An error occurred: {e}")

        # Rollback changes if necessary
        cnx.rollback()

        return -1

    
def save_to_db(order: dict):
    #order = {"pizza": 2, "cholle":1}
    # for food_item, quantity in order.items():
    #     cursor = cnx.cursor()
        
    #     # Executing the SQL query to insert the order details into the orders table
    #     query = f"INSERT INTO orders (order_id, food_item, quantity) VALUES ({get_next_order_id()}, '{food_item}', {quantity});"
    #     cursor.execute(query)
        
    #     # Executing the SQL query to update the order status in the order_tracking table

    # pass

    next_order_id = get_next_order_id()
    for food_item, quantity in order.items():
        rcode = insert_order_item(
            food_item,
            quantity,
            next_order_id

        )
        if rcode == -1:
            return -1
        
    insert_order_tracking(next_order_id,"in progress")
        
    return next_order_id

def insert_order_tracking(order_id, satus):
    cursor = cnx.cursor()

    # Executing the SQL query to insert the order tracking details into the order_tracking table
    query = f"INSERT INTO order_tracking (order_id, status) VALUES ({order_id}, '{satus}');"
    cursor.execute(query)

    # Committing the changes
    cnx.commit()

    # Closing the cursor
    cursor.close()

    print("Order tracking inserted successfully!")


def get_total_order_price(order_id):
    cursor = cnx.cursor()

    # Executing the SQL query to get the total order price
    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    return result
