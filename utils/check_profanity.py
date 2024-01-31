import openai

from pprint import pprint

from utils.env_result import GPTKEY
from utils.logger import LOGGER
from profanity_check import predict, predict_prob

openai.api_key = GPTKEY

def profanity_check(text: str) -> bool:
    """Checks if there is a profanity in the word or sentence sent

    Args:
        text (str): sentence or message provided by the user

    Returns:
        bool: true or false value if the prfanity check agrees or disagrees
    """
    LOGGER.info("Running Profanity CHeck Now")

    try:
        score = predict_prob([text])
        LOGGER.debug(score[0])
        if score[0] > 0.65:
            return True
        return False
    except Exception as e:
        LOGGER.error(str(e))
        return False


def translate_text(text: str, language_iso: str) -> str:
    """Translates the bot response to the chosen language

    Args:
        text (str): sentence or message provided by the user
        language_iso (str): Language choice and selection

    Returns:
        str: translated sentence
    """
    if not language_iso.upper() == "EN":
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"Please translate this highlighted text: '{text}' to {language_iso}"
                },
            ]
        )
        LOGGER.debug(str(response.choices[0].message.content))
        response = str(response.choices[0].message.content)
        return response.title()
    return text


