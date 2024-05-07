
import re
from openai import OpenAI
import emoji
import os
from dotenv import load_dotenv


load_dotenv()


client = OpenAI(
    api_key = os.environ.get("OPENAI"),
)

def extract_emojis(text):
    emoji_pattern = re.compile("["
                            u"\U0001F600-\U0001F64F"  # emoticons
                            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                            u"\U0001F680-\U0001F6FF"  # transport & map symbols
                            u"\U0001F700-\U0001F77F"  # alchemical symbols
                            u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                            u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                            u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                            u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                            u"\U00002702-\U000027B0"  # Dingbats
                            u"\U000024C2-\U0001F251" 
                           "]+", flags=re.UNICODE)
    emojis_list = emoji_pattern.findall(text)
    emojis = ''.join(emojis_list)
    return emojis


def summarizeByEmoji(subject):

    # prompt
    prompt = f"Please express the following email's title using only three emojis.\n{subject}"

    # gpt-3.5-turbo
    completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
            ]
    )

    generated_text = completion.choices[0].message.content
    emojiOnly = extract_emojis(generated_text)

    if len(emojiOnly) >= 3:
            return emojiOnly[:3] 
    else:
        summarizeByEmoji(subject)





# test
# subject = "new product"
# response = summarizeByEmoji(subject)
# print(response)
