import logging
from openai import OpenAI
import json

from models import Scene

OLD_RULES = '''
- DO NOT DESCRIBE THE CHARACTER'S EXPRESSIONS IN THE MAIN IMAGE (ex: looking confused, concerned expression, etc...)
- For main image prompt, pick a shot and angle for the scene, here is the list of possible shots and angles:
   * shots: ["close up shot", "medium shot", "full body shot"]
   * angles: ["front view", "side view", "back view", "wide angle view", "top view"]
'''

STORYBOARD_PROMPT = '''
You are a director creating a storyboard, for each line of the given script, create prompts for a text-to-image model to visualize each scene.

You are given the script for a scene and description of each characters.
Follow these rules:
- Each prompt containing a person should also include their gender and whether they are young, middle aged, or old
- DO NOT SKIP ANY LINES in the story! If a line is too short or too ephemeral to visualize, set the prompt to be "TEXT"
- Keep the image prompts as simple as possible
- Avoid syntactic ambiguity in the prompts
- Return the fields in a JSON dict, "start_ms", "end_ms" and "prompt"
------------
'''

client = OpenAI(
  organization='org-hbiaDN98LaIVi7imbazfaGyX',
  project='proj_Sp83VX6AM4Zsze0iiSwLcGUv',
  api_key='sk-proj-2cdNg1xwjx5OkRA26GkWT3BlbkFJXaWVVWsOdWMHZJNAqLIC'
)

def generate_scenes(story: str):
    # completion = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": STORYBOARD_PROMPT},
    #         {"role": "user", "content": story}
    #     ],
    #     max_tokens=4096,
    #     response_format={"type": "json_object"}
    # )

    try:
        # if completion.choices[0].finish_reason == "length":
        #     print("ERROR: finish reason = length")
        #     print(completion.choices[0].message)
        #     return None

        # scene_config = json.loads(completion.choices[0].message.content)

        # with open('texts/0_scene_config_response.json', 'w') as f:
        #     json.dump(scene_config, f, indent=4)

        # temp
        with open('texts/0_scene_config_response.json', 'r') as f:
            scene_config = json.load(f)
        
        scenes = []
        for scene_no, scene_data in enumerate(scene_config["scenes"]):
            scene = Scene(
                id=scene_no,
                **scene_data
            )
            scenes.append(scene)
            
        return scenes
    except Exception as e:
        logging.exception(e)
