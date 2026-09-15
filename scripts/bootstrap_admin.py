import asyncio
from getpass import getpass

from app.core.exceptions import (
    RoleNotFoundError,
    UserAlreadyExistsError,
)
from app.db.session import AsyncSessionFactory
from app.schemas.user import UserCreate
from app.services.user import UserService


async def main() -> None:
    print("Create initial administrator")
    print()

    full_name = input("Full name: ").strip()
    email = input("Email: ").strip()
    password = getpass("Password: ")
    password_confirmation = getpass(
        "Confirm password: ",
    )

    if password != password_confirmation:
        print("Passwords do not match.")
        return

    data = UserCreate(
        full_name=full_name,
        email=email,
        password=password,
        role_name="admin",
    )

    async with AsyncSessionFactory() as db:
        service = UserService(db)

        try:
            user = await service.create_user(data)

        except RoleNotFoundError:
            print("Admin role does not exist. Create the 'admin' role first.")
            return

        except UserAlreadyExistsError:
            print("A user with this email already exists.")
            return

    print()
    print(f"Admin created successfully: {user.email}")


if __name__ == "__main__":
    asyncio.run(main())
