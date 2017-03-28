#!/usr/bin/env python
# -*- coding: utf-8 -*-
import vk
import urllib2
import requests
import json
import giphypop

# gif = giphypop.Giphy()
# result = gif.search('pony')
# print gif.screensaver('random_gif').media_url
# for i in gif.screensaver('random_gif'):
#     print i
apiuser = vk.API(vk.Session(access_token="2307738536e2aa23882ae54c514564ba67fe87aeea98e7247af48ca71030dbe97102322fb736c1cf86a7c"), v='5.63', timeout=30)

print apiuser.users.get()


# api = vk.API(vk.Session(access_token="740f3f24062cf595ba12a8e5862c270814f4a5d7d7ab2a4001c5c45438d1881dea2d3d79124b4d0b670aa"), v='5.63', timeout=30)
# apiuser = vk.API(vk.Session(access_token="24909712c7fe27026da1dd7de2fbc092149f6acea3859db0d8c8ca20a04472544debe3766873527f224d2"), v='5.63', timeout=30)
#
# url = 'https://media.giphy.com/media/wlJsTzy11bLMc/giphy.gif'
# gif = requests.get(url,stream=True)
# if gif.status_code == 200:
#     uploadurl = api.docs.getWallUploadServer(group_id=141410969)['upload_url']
#     responsefileuploaded = requests.post(uploadurl, files={'file':('file.gif', gif.raw)})
#     responsefileuploadeds = json.loads(responsefileuploaded.text)
#     print '|'.join(responsefileuploadeds['file'].split('|')[:9])+'|'
#     file = '%s'% responsefileuploadeds['file']
#     if 'file' in responsefileuploaded.text:
#         saved = apiuser.docs.save(file=file)
#         print saved
