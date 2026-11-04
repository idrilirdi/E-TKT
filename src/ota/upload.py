# Allows PlatformIO to upload directly to ElegantOTA v3
# Based on the AsyncElegantOTA upload script:
# https://github.com/ayushsharma82/AsyncElegantOTA
# ElegantOTA v3 first takes the MD5 at /ota/start, then the file at /ota/upload.
#
# To use, set the following for your project in platformio.ini:
#
# extra_scripts = <path_to_this_script>
# upload_protocol = custom
# upload_url = http://e-tkt.local # or access by ip address

import requests
import hashlib
Import('env')

try:
    from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
    from tqdm import tqdm
except ImportError:
    env.Execute("$PYTHONEXE -m pip install requests_toolbelt")
    env.Execute("$PYTHONEXE -m pip install tqdm")
    from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
    from tqdm import tqdm

def on_upload(source, target, env):
    firmware_path = str(source[0])
    upload_url = env.GetProjectOption('upload_url').rstrip('/')

    with open(firmware_path, 'rb') as firmware:
        md5 = hashlib.md5(firmware.read()).hexdigest()
        firmware.seek(0)

        start = requests.get(upload_url + '/ota/start',
                             params={'mode': 'fr', 'hash': md5})
        if start.status_code != 200:
            print(start, start.text)
            return 1

        encoder = MultipartEncoder(fields={
            'file': ('firmware.bin', firmware, 'application/octet-stream')}
        )

        bar = tqdm(desc='Upload Progress',
              total=encoder.len,
              dynamic_ncols=True,
              unit='B',
              unit_scale=True,
              unit_divisor=1024
              )

        monitor = MultipartEncoderMonitor(encoder, lambda monitor: bar.update(monitor.bytes_read - bar.n))

        response = requests.post(upload_url + '/ota/upload', data=monitor, headers={'Content-Type': monitor.content_type})
        bar.close()
        print(response,response.text)
            
env.Replace(UPLOADCMD=on_upload)