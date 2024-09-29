import io

from constants import FLUX_SCHNELL_REGULAR_PROMPT_TEXT, FLUX_SCHNELL_SIMPLE_PROMPT_TEXT, IMAGES_DIR, OUTPUT_DIR
import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse

from PIL import Image
from models import Scene
from utils import ensure_directory_exists

class TextToImage:
    def __init__(self) -> None:
        self.server_address = "127.0.0.1:8188"
        self.client_id = str(uuid.uuid4())
        self.ws = websocket.WebSocket()
        self.ws.connect("ws://{}/ws?clientId={}".format(self.server_address, self.client_id))
    
    def __del__(self):
        self.ws.close()
        
    def generate_images(self, scene: Scene):
        scene_image_dir = f'{OUTPUT_DIR}/p{scene.id}/{IMAGES_DIR}'
        ensure_directory_exists(scene_image_dir)
        
        for prompt in scene.image_prompts:
            prompt.path = f"{scene_image_dir}/{prompt.start_ms}_{prompt.end_ms}.png"
            self.generate(prompt.prompt, prompt.path)

    def generate(self, prompt_text: str, output_path: str):
        prompt = json.loads(FLUX_SCHNELL_SIMPLE_PROMPT_TEXT)

        prompt["6"]["inputs"]["text"] = prompt_text + ', Edward Hopper style black and white rough sketch'
        images = self.get_images(self.ws, prompt)

        for node_id in images:
            for image_data in images[node_id]:
                image = Image.open(io.BytesIO(image_data))
                            
                # Save the image
                image.save(output_path)
                print(f"Image saved to {output_path}")
        
        return output_path
    
    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(self.server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())
    
    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(self.server_address, url_values)) as response:
            return response.read()
        
    def get_history(self, prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(self.server_address, prompt_id)) as response:
            return json.loads(response.read())
        
    def get_images(self, ws, prompt):
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                continue #previews are binary data

        history = self.get_history(prompt_id)[prompt_id]
        
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
            output_images[node_id] = images_output

        return output_images


def generate_sd(prompt: str, output_path: str, attempt_no: int):
    url = "http://127.0.0.1:7860"
    payload = {
        "prompt": f"<lora:storyboard sketch:1> {prompt}",
        "negative_prompt": "(extra characters), (extra people), (color), text, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, (extra fingers), (mutated hands), poorly drawn hands, poorly drawn face, mutation, deformed, blurry, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, (fused fingers), (too many fingers), long neck, camera",
        "sampler_name": "DPM++ 2M SDE",
        "scheduler": "exponential",
        "steps": 20,
        "cfg_scale": 7,
        "width": 1024,
        "height": 1024,
    }
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

    if response.status_code != 200:
        if attempt_no == 3:
            raise Exception("Non-200 response: " + str(response.text))
        
        print(f"ERROR | text to speech | {response.text} | regenerating")
        generate(prompt, output_path, attempt_no + 1)
    
    data = response.json()

    image = data["images"][0]
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(image))
        print(f"Image saved as ", output_path)
    
    return output_path