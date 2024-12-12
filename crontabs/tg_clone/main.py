import asyncio
from inspect import isawaitable

from telethon import TelegramClient, errors

from cores.config import settings
from cores.log import LOG

API_ID = settings.tg.api_id
API_HASH = settings.tg.api_hash
PHONE = settings.tg.phone
SESSION_FILE = settings.tg.session_file

# Create Telegram client
client = TelegramClient(SESSION_FILE, API_ID, API_HASH, timeout=3)


async def main():
    try:
        # Attempt to start the client and get user info
        conn = client.start(phone=PHONE)
        if isawaitable(conn):
            await conn

        me = await client.get_me()

        LOG.info("User Details:")
        LOG.info(f"ID: {me.id}")
        LOG.info(f"Username: {me.username}")
        LOG.info(f"Phone: {me.phone}")
        LOG.info(f"First Name: {me.first_name}")
        LOG.info(f"Last Name: {me.last_name}")

        # Get recent dialogs
        LOG.info("Recent Dialogs:")
        async for dialog in client.iter_dialogs(limit=10):
            LOG.info(f"{dialog.name} ({dialog.entity.id})")

    except errors.SessionPasswordNeededError:
        LOG.error("Two-step verification is enabled. Please provide the password.")
    except errors.PhoneCodeInvalidError:
        LOG.error("The provided phone code is invalid.")
    except errors.PhoneNumberInvalidError:
        LOG.error("The provided phone number is invalid.")
    except Exception as e:
        LOG.error(f"An unexpected error occurred: {e}")
    finally:
        await client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
