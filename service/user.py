from bilibili_api import user
from credential import credential
from bilibili_api.utils.network import Api

SelfUser = user.User(credential.dedeuserid, credential)

async def is_follow(uid):
    SelfUser.credential.raise_for_no_sessdata()
    api = {
      "url": "https://api.bilibili.com/x/space/wbi/acc/relation",
      "method": "GET",
      "params": {
        "mid": "int: uid"
      },
      "wbi": True,
      "verify": True,
      "comment": "获取与某用户的关系"
    }
    params = {"mid": uid}
    resp = await Api(**api, credential=SelfUser.credential).update_params(**params).result
    # print(resp)
    return (
      resp["be_relation"]["mid"] != 0
    )

# {'relation': {'mid': 14249358, 'attribute': 6, 'mtime': 1705737781, 'tag': None, 'special': 0}, 'be_relation': {'mid': 1887128032, 'attribute': 6, 'mtime': 1647341237, 'tag': [-10, 451905], 'special': 1}}