# Import necessary modules
from fastapi import APIRouter, HTTPException, Depends
from prisma import Prisma

# Import user model and serialization functions
from app.user.model import UserModel as User
from app.user.schema import individual_serial, list_serial

# Create a router for user-related endpoints
# This allows us to group and organize our user-related API routes
router = APIRouter(prefix="/users", tags=["users"])


# Define a dependency to get a Prisma database client
# This function will be used to inject a database connection into our route handlers
async def get_prisma():
    # Create a new Prisma client
    prisma = Prisma()
    # Connect to the database
    await prisma.connect()
    try:
        # Yield the connected client to be used in the route
        yield prisma
    finally:
        # Ensure the database connection is closed after the request is processed
        await prisma.disconnect()


# Define an endpoint to get all users
@router.get("/")
async def get_users(prisma: Prisma = Depends(get_prisma)):
    """
    Retrieve all users from the database.
    """
    try:
        # Fetch all users from the database
        users = await prisma.user.find_many()
        # Serialize the list of users and return it
        return list_serial(users)
    except Exception as e:
        # If an error occurs, raise an HTTP exception with a 400 status code
        raise HTTPException(status_code=400, detail=str(e))


# Define an endpoint to get a specific user by ID
@router.get("/{user_id}")
async def get_user(
    user_id: str,  # The ID of the user to retrieve, passed in the URL
    prisma: Prisma = Depends(get_prisma),  # Inject the Prisma client
):
    """
    Retrieve a specific user by their ID.
    """
    try:
        # Attempt to find the user in the database
        user = await prisma.user.find_unique(where={"uid": user_id})
        if user is None:
            # If the user is not found, raise a 404 Not Found exception
            raise HTTPException(status_code=404, detail="User not found")
        # If found, serialize and return the user data
        return individual_serial(user)
    except Exception as e:
        # For any other errors, raise a 400 Bad Request exception
        raise HTTPException(status_code=400, detail=str(e))


# Define an endpoint to update a user's information
@router.put("/{user_id}")
async def update_user(
    user_id: str,  # The ID of the user to update, passed in the URL
    user_data: User,  # The new user data, passed in the request body
    prisma: Prisma = Depends(get_prisma),  # Inject the Prisma client
):
    """
    Update a user's information in the database.
    """
    try:
        # Attempt to update the user in the database
        updated_user = await prisma.user.update(
            where={"uid": user_id},  # Specify which user to update
            data={"first_name": user_data.first_name, "email": user_data.email},
        )
        # Serialize and return the updated user data
        return individual_serial(updated_user)
    except Exception as e:
        # If an error occurs (e.g., user not found), raise a 400 Bad Request exception
        raise HTTPException(status_code=400, detail=str(e))


# Define an endpoint to delete a user
@router.delete("/{user_id}")
async def delete_user(
    user_id: str,  # The ID of the user to delete, passed in the URL
    prisma: Prisma = Depends(get_prisma),  # Inject the Prisma client
):
    """
    Delete a user from the database.
    """
    try:
        # Attempt to delete the user from the database
        deleted_user = await prisma.user.delete(where={"uid": user_id})
        # Return a success message
        return {"message": f"User {deleted_user.uid} has been deleted"}
    except Exception as e:
        # If an error occurs (e.g., user not found), raise a 400 Bad Request exception
        raise HTTPException(status_code=400, detail=str(e))
