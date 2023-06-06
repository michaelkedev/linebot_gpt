from __future__ import unicode_literals
import os
import openai
import requests

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

app = Flask(__name__)


line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))

openai.api_key = os.getenv("OPENAI_API_KEY")

stable_diffusion_api = os.getenv("STABLE_DIFFUSION_API_KEY")

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        ## Chatgpt
        # response = openai.Completion.create(
        #     model="text-davinci-003",
        #     prompt=event.message.text,
        #     max_tokens=128,
        #     temperature=0.5,
        # )

        # ans = response["choices"][0]["text"]
        # print(response['choices'])
        try:
            payload = {
                "key": stable_diffusion_api,
                "prompt": event.message.text,
                "negative_prompt": "((out of frame)), ((extra fingers)), mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), (((tiling))), ((naked)), ((tile)), ((fleshpile)), ((ugly)), (((abstract))), blurry, ((bad anatomy)), ((bad proportions)), ((extra limbs)), cloned face, (((skinny))), glitchy, ((extra breasts)), ((double torso)), ((extra arms)), ((extra hands)), ((mangled fingers)), ((missing breasts)), (missing lips), ((ugly face)), ((fat)), ((extra legs))",
                "width": "512",
                "height": "512",
                "samples": "1",
                "num_inference_steps": "20",
                "safety_checker": "no",
                "enhance_prompt": "yes",
                "seed": None,
                "guidance_scale": 7.5,
                "webhook": None,
                "track_id": None
            }
            
            print("Generating........")

            response = requests.post("https://stablediffusionapi.com/api/v3/text2img", params=payload)
            
            print(response)

            response2json = response.json()

            print(response2json)

            img_url = response2json["output"][0]
        # TextSendMessage(text= f"{img_url}")

            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=f"{img_url}",
                    preview_image_url=f"{img_url}"
                )
            )
        except Exception as e:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Something went wrong. Please try again.")
            )

if __name__ == "__main__":
    app.run()