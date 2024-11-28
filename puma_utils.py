def list_bib(search_string = None, owner_username=None, year=None, verbose=False):
    import requests
    import base64
    import os

    # Get credentials from environment variables
    USERNAME = os.environ.get('PUMA_USERNAME')
    API_KEY = os.environ.get('PUMA_API_KEY')
    
    # Create authentication header
    auth_string = f"{USERNAME}:{API_KEY}"
    auth_bytes = auth_string.encode('ascii')
    base64_auth = base64.b64encode(auth_bytes).decode('ascii')
    headers = {'Authorization': f'Basic {base64_auth}'}
    
    # Get all posts of a given user
    url = f"https://puma.scadsai.uni-leipzig.de/api/posts?resourcetype=bibtex&format=json&end=2000"
    if search_string is not None:
        url += "&search=" + search_string
    if owner_username is not None:
        url += "&user=" + owner_username
    if year is not None:
        if not isinstance(year, list):
            year = [year]
        if isinstance(year, tuple) and len(year) == 2:
            year = list(range(year[0], year[1] + 1))
    
    # Make the request
    response = requests.get(url, headers=headers)
    
    # Check if request was successful
    if response.status_code == 200:
        data = response.json()
    
        bibtex_entries = []
        for pub in list(data["posts"]["post"]):

            bibtex = pub['bibtex']
            
            title = bibtex.get('title', '')
            if verbose:
                print(title)

            if "bibtexKey" in bibtex.keys():
                cite_key = bibtex["bibtexKey"]
            else:
                cite_key = bibtex.get('title', '').split()[0].lower() + bibtex['year']
            entrytype = bibtex['entrytype']

            if year is not None:
                article_year = int(bibtex['year'])
                if not article_year in year:
                    continue
            
            bibtex = f"@{entrytype}{{{cite_key},\n"
            for key, value in pub['bibtex'].items():
                if key not in ['cites', 'intrahash', 'interhash', 'href', 'bibtexAbstract', 'entrytype', 'bibtexKey']:
                    bibtex += f"  {key} = {{{value}}},\n"
            bibtex += "}"
            bibtex_entries.append(bibtex)
        return bibtex_entries
    else:
        print(response.text)

    