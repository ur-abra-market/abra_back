import asyncio

from population import loader, data_generator


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(loader.load_constants())
    loop.run_until_complete(data_generator.load_all())
