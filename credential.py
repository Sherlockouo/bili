from bilibili_api import Credential, sync, login, user, exceptions
import os
import json

credential = Credential()

# Check if credential file exists
credential_file = './.credential'
if not os.path.exists(credential_file) and os.path.getsize(credential) == 0 :
    # If credential file does not exist, login via QR Code
    try:
        credential = login.login_with_qrcode_term()
        print('credential ',credential)
        # On successful login, store the credential object
        with open(credential_file, 'w') as f:
            json.dump({
                'sessdata': credential.sessdata,
                'bili_jct': credential.bili_jct,
                'buvid3': credential.buvid3,
                'dedeuserid': credential.dedeuserid,
                'ac_time_value': credential.ac_time_value
            }, f)
    except exceptions.BilibiliApiException:
        print("An exception occurred while logging in.")
else:
    # If credential file exists, load the credentials
    with open(credential_file, 'r') as f:
        creds = json.load(f)
        credential = Credential(
            sessdata=creds['sessdata'],
            bili_jct=creds['bili_jct'], 
            buvid3=creds['buvid3'],
            dedeuserid=creds['dedeuserid'],
            ac_time_value=creds['ac_time_value']  
        )

# print("Credential: ", credential)

# # 检查 Credential 是否需要刷新
# if sync(credential.check_refresh()):
#     # 刷新 Credential
#     sync(credential.refresh())

# session = Session(credential)

# sync(session.start())