
from gssutils import Scraper
import json
import traceback
import sys
import os
import requests  # probably dont need this, investigate

from parser import parse_scrape_to_json

def serve_main_page():

    # Nasty hack to get a single endpoint to (re)call itself with params
    THIS_URL = os.environ["THIS_URL"]

    return """
    <!DOCTYPE html>
    <html>
    <body>

    <h2>Scraper Trial UI</h2>

    <form action="{}">
      Scrape a link and and you'll get one of:<br>
      <ul>
        <li>If we have a scraper and it works, you'll get a json document showing what it scraped.</li>
        <li>If we don't have a scraper, it'll say.</li>
        <li>If you get a different error, it's broke, or this tool is.</li>
    </ul>
      <br>
      Url:<br>
      <input type="text" name="target-url" width="100">

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

        # Get the full list of supported scrapers
        try:
            r = requests.get("https://raw.githubusercontent.com/GSS-Cogs/gss-utils/master/gssutils/scrapers/__init__.py")
            if r.status_code != 200:
                raise Exception("Failed to get deployed scraper urls from github")

            text_dump = r.text
            take = False
            urls = []
            for line in text_dump.split("\n"):
                if "https" in line:
                    urls.append(line.split("('")[1].split(",")[0])  # ewww
        except:
            urls = ["...unable to acquire..."]

        # Give some sort of meanigful feedback
        trace = traceback.print_exc(file=sys.stdout)
        return """
        <h3>Failure for url: {url}</h3>
        <hr>
        {trace}
        <br>
        {e}
        <br>
        The following are deployed scrapers that -should- work on every release of a given dataset.
        {urls}
        Failing that, a basic "one off" scrape can be taken provided sufficiant explicit metadata
        for the following fields is provided:  "title", "description", "dataURL", "publisher", "published".
        <br>
        """.format(url=url, e=e, trace=trace, urls="\n".join(urls))

def main(request):

    os.chdir('/tmp') # otherwise the cacher will blow up as the other paths
                     # on a cloud function are read only.

    try:
        # If url params contain "target-url" we're aiming to scrape
        url = request.args.get('target-url')
        if url != "" and url != None:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://"+url
            return serve_result_page(url)
    except:
        raise

    # Server the splash page
    return serve_main_page()
