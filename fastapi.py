@app.post("/explorer/{path:path}", include_in_schema=False)
async def post_handler(request: Request, path: str):
    internal_url = f"http://192.168.1.41:80/{path}"
    form_data = await request.form()
    async with httpx.AsyncClient() as client:
        response = await client.post(internal_url, data=form_data)
 
        # If the response is a redirect and the content type is text (plain text response)
        if response.status_code in (302, 307) and 'text/plain' in response.headers.get('Content-Type', ''):
            # Extract the redirect location from the response content
            redirect_location = response.text.split(' ')[-1]
            # Ensure the redirect location starts with '/explorer/'
            if not redirect_location.startswith('/explorer/'):
                redirect_location = '/explorer' + redirect_location
 
            # Construct an HTML response with a meta refresh tag for redirection
            html_content = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <meta http-equiv="refresh" content="0;url={redirect_location}" />
                    <style>
                        body {{
                            background-color: black;
                            color: white;
                            font-family: Arial, sans-serif;
                            text-align: center;
                            padding-top: 50px;
                        }}
                        a {{
                            color: lightblue;
                        }}
                    </style>
                </head>
                <body>
                    <p>Searching Block Chain Records...</p>
                </body>
            </html>
            """
            return HTMLResponse(content=html_content)
 
        if 'text/html' in response.headers.get('Content-Type', ''):
            soup = BeautifulSoup(response.content, 'html.parser')
 
            # Define the base URL
            base_url = "https://nanocheeze.com"
 
            # Modify AJAX URLs in script tags
            for script in soup.find_all('script'):
                if script.string:
                    # Replace relative AJAX paths with absolute paths
                    script.string = script.string.replace("'/ext/", f"'{base_url}/explorer/ext/")
 
                if script.get('src'):
                    script['src'] = correct_path(script['src'])
 
            # Modify link paths
            for link in soup.find_all('link', href=True):
                link['href'] = correct_path(link['href'])
 
            # Modify block paths in 'a' tags
            for a_tag in soup.find_all('a', href=True):
                a_tag['href'] = correct_path(a_tag['href'])
 
            # Modify image paths in 'img' tags
            for img_tag in soup.find_all('img', src=True):
                img_tag['src'] = correct_path(img_tag['src'])
 
 
            # Update the action attributes of form tags for correct redirection
            for form in soup.find_all('form', action=True):
                # Normalize the form action path and ensure it starts with '/explorer/'
                form_action = form['action'].lstrip('/')
                if form['action'].endswith('/search'):
                    form['action'] = 'https://nanocheeze.com/explorer/search'
                else:
                    form['action'] = correct_path('/' + form_action)
 
            modified_content = str(soup).encode()
            return Response(content=modified_content, media_type='text/html')
 
        return Response(content=response.content, media_type=response.headers["Content-Type"])
 
@app.get("/explorer/{path:path}", include_in_schema=False)
async def reverse_proxy(path: str):
    internal_url = f"http://192.168.1.41:80/{path}"
    async with httpx.AsyncClient() as client:
 
        response = await client.get(internal_url)
 
        if 'text/html' in response.headers.get('Content-Type', ''):
            soup = BeautifulSoup(response.content, 'html.parser')
 
            # Update the href attributes of link tags
            for link in soup.find_all('link', href=True):
                link['href'] = correct_path(link['href'])
 
            for link in soup.find_all('a', href=True):
                if 'explorer.nanocheeze.com' in link.text and 'api/' not in link.text:
                    link.string = link.text.replace('explorer.nanocheeze.com', 'nanocheeze.com/explorer')
                    link.string = link.text.replace('f2d30bda6276ac986d7231f6f47673ccd304bd454492fbf684b7d7605f10feeb', '97744b2936b301fa80195ad0daccf71139e94edddcf5b1380e86ac1c303b2a87')
 
            for link in soup.find_all('a', href=True):
                if 'f2d30bda6276ac986d7231f6f47673ccd304bd454492fbf684b7d7605f10feeb' in link['href']:
                    link['href'] = link['href'].replace('f2d30bda6276ac986d7231f6f47673ccd304bd454492fbf684b7d7605f10feeb', '97744b2936b301fa80195ad0daccf71139e94edddcf5b1380e86ac1c303b2a87')
 
            # Update the src attributes of img tags
            for img in soup.find_all('img', src=True):
                img['src'] = correct_path(img['src'])
 
            # Update the href attributes of anchor tags for internal navigation
            for anchor in soup.find_all('a', href=True):
                anchor['href'] = correct_path(anchor['href'])
 
            # Update the action attributes of form tags for correct redirection
            for form in soup.find_all('form', action=True):
                # Normalize the form action path and ensure it starts with '/explorer/'
                form_action = form['action'].lstrip('/')
                if form['action'].endswith('/search'):
                    form['action'] = 'https://nanocheeze.com/explorer/search'
                else:
                    form['action'] = correct_path('/' + form_action)
 
            # Update the src attributes of script tags and modify AJAX calls within scripts
            for script in soup.find_all('script', src=True):
                script['src'] = correct_path(script['src'])
 
            # Update the meta og:image content
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.has_attr('content'):
                og_image['content'] = correct_path(og_image['content'])
 
            for script in soup.find_all('script'):
                if script.string:
                    script.string = correct_ajax_path(script.string)
 
            # Update the text of API links to reflect the correct base URL
            for api_link in soup.find_all('a', href=True):
                if api_link['href'].startswith('/api/'):
                    # Correct the href for API links
                    api_link['href'] = correct_path(api_link['href'])
                    # Correct the text for API links if it contains the incorrect URL
                    if 'explorer.nanocheeze.com' in api_link.text:
                        api_link.string = api_link.text.replace('explorer.nanocheeze.com', 'nanocheeze.com')
                        api_link.string = api_link.text.replace('f2d30bda6276ac986d7231f6f47673ccd304bd454492fbf684b7d7605f10feeb', '97744b2936b301fa80195ad0daccf71139e94edddcf5b1380e86ac1c303b2a87')
 
            modified_content = str(soup).encode()
            return HTMLResponse(content=modified_content, media_type='text/html')
 
        return Response(content=response.content, media_type=response.headers["Content-Type"])
def correct_ajax_path(script_content: str):
    # This function replaces incorrect AJAX paths in the script content
    corrected_script = script_content.replace("url: '/ext/", "url: '/explorer/ext/")
    return corrected_script
 
def correct_path(url: str):
    if url.startswith('http://') or url.startswith('https://'):
        return url
    elif url.startswith('//'):
        return url
    elif url.startswith('/api/'):
        # Keep /api/ paths directly without adding /explorer
        return url
    elif url.startswith('/'):
        return '/explorer' + url
    elif url.startswith('../'):
        return '/explorer/' + url.lstrip('./')
    else:
        return '/explorer/' + url
 
@app.get("/tx/{path:path}", include_in_schema=False)
async def redirect_tx_to_explorer(request: Request, path: str):
    new_url = str(request.url).replace('/tx/', '/explorer/tx/')
    return RedirectResponse(url=new_url, status_code=307)  # Temporary Redirect
 
@app.get("/block{path:path}", include_in_schema=False)
async def redirect_block_to_explorer(request: Request, path: str):
    new_url = str(request.url).replace('/block/', '/explorer/block/')
    return RedirectResponse(url=new_url, status_code=307)  # Temporary Redirect
 
@app.get("/search{path:path}", include_in_schema=False)
async def redirect_search_to_explorer(request: Request, path: str):
    # Constructing the new URL with the '/explorer/search' prefix
    new_url = request.url_for('get_handler', path=f"search{path}").replace('/search', '/explorer/search')
    return RedirectResponse(url=new_url, status_code=307)  # Temporary Redirect
 
@app.post("/search{path:path}", include_in_schema=False)
async def redirect_post_search_to_explorer(request: Request, path: str):
    # For POST requests on search, ensuring redirection includes '/explorer'
    new_url = request.url_for('post_handler', path=f"search{path}").replace('/search', '/explorer/search')
    return RedirectResponse(url=new_url, status_code=307)  # Temporary Redirect
 
@app.post("/search", include_in_schema=False)
async def redirect_post_search_to_explorer(request: Request, path: str):
    # For POST requests on search, ensuring redirection includes '/explorer'
    new_url = request.url_for('post_handler', path=f"search{path}").replace('/search', '/explorer/search')
    return RedirectResponse(url=new_url, status_code=307)  # Temporary Redirect
 
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")
 
@app.api_route("/api/{path:path}", methods=["GET", "POST"], include_in_schema=False)
async def api_forward_and_serve(request: Request, path: str):
    # Define the target URL
    target_url = f"http://explorer.nanocheeze.com/api/{path}"
 
    try:
        # Prepare the headers for the new request, excluding the Host
        headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
 
        async with httpx.AsyncClient() as client:
            if request.method == "GET":
                # Forward the query parameters and make the GET request to the target URL
                response = await client.get(target_url, headers=headers, params=request.query_params)
            else:
                # For POST, forward the body
                body = await request.body()
                response = await client.post(target_url, headers=headers, content=body)
 
        # Check for a successful response
        if response.status_code == 200:
            # Return the content from the target API as the response content
            return Response(content=response.content, media_type=response.headers["Content-Type"])
        else:
            # Handle non-200 responses
            return Response(f"Received a {response.status_code} response from the target API", status_code=response.status_code)
 
    except httpx.RequestError as exc:
        # Handle request errors to the target API
        return Response(f"An error occurred while requesting {exc.request.url!r}.", status_code=500)
    except Exception as exc:
        # Handle any other errors
        return Response(f"An internal server error occurred: {exc}", status_code=500)
 
