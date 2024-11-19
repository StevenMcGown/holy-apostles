import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_saints_by_date(date=None):
    """Fetches the saints' paragraph for today's date from the OCA website."""
    if date is None:
        date = datetime.now()
    formatted_date = date.strftime("%Y/%m/%d")  # Format as YYYY/MM/DD
    url = f"https://www.oca.org/readings/daily/{formatted_date}"

    try:
        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate the section with the readings
        section = soup.find('section')
        if section:
            # Extract the saints paragraph following the header
            saints_header = section.find('h3', string="Today’s commemorated feasts and saints")
            if saints_header:
                saints_paragraph = saints_header.find_next('p')
                if saints_paragraph:
                    return saints_paragraph.get_text(strip=True)
                else:
                    return "No saints paragraph found."
            else:
                return "No saints header found."
        else:
            return "No readings section found."
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Allow the script to be executed directly for testing
if __name__ == "__main__":
    print(get_saints_by_date())
