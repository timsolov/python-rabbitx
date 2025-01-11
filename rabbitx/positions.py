from rabbitx.private_request import rabbit_private_requestion

def get_positions(tg_id:str):
    """Get all positions for a given user.
    
    Args:
        tg_id (str): Telegram ID of the user
        
    Returns:
        dict: JSON response containing positions if successful, None otherwise
    """
    response = rabbit_private_requestion(
        tg_id=tg_id,
        endpoint="/positions",
        method='get'
    )
    
    if response.status_code == 200:
        return response.json()
    
    return None


    

