from scrape_site import get_saints_by_date
from datetime import datetime
from openai import OpenAI
import json
import os

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
    # Example: Use today's date
    # today = datetime.now()
    # saints_today = get_saints_by_date(today)
    today = datetime(2023, 1, 5)
    saints_today = get_saints_by_date(today)

    # Load stream titles and dates from JSON file
    try:
        with open("stream_titles.json", "r") as json_file:
            stream_titles = json.load(json_file)
    except FileNotFoundError:
        print("Error: The file 'stream_titles.json' was not found.")
        return
    except json.JSONDecodeError:
        print("Error: The file 'stream_titles.json' contains invalid JSON.")
        returns

    # Create OpenAI query content
    query_content = f"""
    You are tasked with creating a YouTube livestream title for an Orthodox Church stream. Please adhere to the following guidelines and constraints:

    1. **Naming Format**: The title must be based on the naming format of previous livestream titles.
    2. **Context**: Today's date is {today}.
    - Divine Liturgy occurs on Sunday.
    - Great Vespers occurs on Wednesday.
    - Saturday is for Saturday Vigil.
    3. **Character Limit**: The title must stay **under 70 characters** to ensure readability.
    4. **Previous Titles for Reference**: Below is a list of previous livestream titles. Use this as inspiration to maintain consistency.
    ### PREVIOUS STREAM TITLES ###
    {stream_titles}
    5. **Today's Saints Information**: Use the information from the OCA website to craft a meaningful and relevant title.
    ### SAINTS INFORMATION ###
    {saints_today}

    ### Task ###
    - Generate a single title string based on the above criteria.
    - Respond with only the title string and nothing else.
    """


    # Send query to OpenAI
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates stream titles for an American Orthodox Church YouTube live stream."},
            {"role": "user", "content": query_content}
        ]
    )

    # Print the response
    print("OpenAI Response:")
    print(response.choices[0].message.content.strip())

if __name__ == "__main__":
    main()
