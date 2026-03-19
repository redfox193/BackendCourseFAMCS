import asyncio

import aiohttp


BASE_URL = "http://localhost:8080"


async def list_todos(session: aiohttp.ClientSession) -> None:
    async with session.get(f"{BASE_URL}/todos") as resp:
        data = await resp.json()
        print(f"\nStatus: {resp.status}")
        print("Todos:")
        if not data:
            print("  (empty)")
        else:
            for tid, text in data.items():
                print(f"  {tid}: {text}")


async def add_todo(session: aiohttp.ClientSession) -> None:
    text = input("Enter todo text: ").strip()
    if not text:
        print("Text cannot be empty")
        return

    async with session.post(f"{BASE_URL}/todos", json={"text": text}) as resp:
        data = await resp.json()
        print(f"\nStatus: {resp.status}")
        print("Current todos:")
        for tid, t in data.items():
            print(f"  {tid}: {t}")


async def edit_todo(session: aiohttp.ClientSession) -> None:
    todo_id = input("Enter todo id to edit: ").strip()
    text = input("Enter new text: ").strip()
    if not text:
        print("Text cannot be empty")
        return

    async with session.put(f"{BASE_URL}/todos/{todo_id}", json={"text": text}) as resp:
        data = await resp.json()
        print(f"\nStatus: {resp.status}")
        print(data)


async def delete_todo(session: aiohttp.ClientSession) -> None:
    todo_id = input("Enter todo id to delete: ").strip()

    async with session.delete(f"{BASE_URL}/todos/{todo_id}") as resp:
        data = await resp.json()
        print(f"\nStatus: {resp.status}")
        print(data)


def print_menu() -> None:
    print(
        """
==== Todo client ====
1) List todos
2) Add todo
3) Edit todo
4) Delete todo
5) Exit
"""
    )


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        while True:
            print_menu()
            choice = input("Choose option: ").strip()

            if choice == "1":
                await list_todos(session)
            elif choice == "2":
                await add_todo(session)
            elif choice == "3":
                await edit_todo(session)
            elif choice == "4":
                await delete_todo(session)
            elif choice == "5":
                print("Bye")
                break
            else:
                print("Unknown option")

            print()


if __name__ == "__main__":
    asyncio.run(main())
