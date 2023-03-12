import aiohttp


class PyMyGekko:
    def __init__(self, username: str, apiKey: str, gekkoId: str) -> None:
        self.url = "https://live.my-gekko.com/api/v1/var"
        self.username = username
        self.apiKey = apiKey
        self.gekkoId = gekkoId

    async def try_connect(self):
        params = {
            "username": self.username,
            "key": self.apiKey,
            "gekkoid": self.gekkoId,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, params=params) as resp:
                print(resp.status)
                print(await resp.text())
                return resp.status
