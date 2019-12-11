
from gssutils import Scraper
import json
import traceback
import sys
import os

from parser import parse_scrape_to_json

def serve_main_page():
    THIS_URL = os.environ["THIS_URL"]
    return """
    <!DOCTYPE html>
    <html>
    <body>

    <h2>Simple Scraper Form</h2>

    <form action="{this_url}">
      Try and scrape a link and see what happens:<br>
      <br>
      Url:<br>
      <input type="text" name="target-url" width:100%>

      <input type="submit" value="Submit">
    </form>

    <br>
    <br>
    <br>

    </body>
    </html>
    """.format(THIS_URL)

def serve_result_page(url):

    try:
        scrape = Scraper(url)
        json_dict = parse_scrape_to_json(scrape)
        return json.dumps(json_dict)

    except Exception as e:
        trace = traceback.print_exc(file=sys.stdout)
        return """
        <h3>Failure for url: {url}</h3>
        <hr>
        {trace}
        <br>
        {e}
        """.format(url=url, e=e, trace=trace)

def main(request):

    try:
        url = request.args.get('target-url')
        if url != "" and url != None:

            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://"+url

            return serve_result_page(url)
    except:
        raise

    return serve_main_page()