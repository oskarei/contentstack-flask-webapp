###
# Getting content from Contentstack to use within Flask
# https://contentstack.com
# Created: 2020-03-06
# @author: oskar.eiriksson@contentstack.com
###
import os
import contentstack

# Establishing connection with Contentstack using variables defined in .flaskenv
api_key = os.getenv('APIKEY', None)
delivery_token = os.getenv('DELIVERYTOKEN', None)
environment = os.getenv('ENVIRONMENT', None)
config = contentstack.Config()
config.region = contentstack.config.ContentstackRegion.EU # Enum // Contentstack offers both US and EU. Confirm where your stack is. US is the default one.


def initStack():
    '''
    Bug. Seems I have to initialize the stack every time.
    Otherwise results are not to be trusted.
    '''
    stack = contentstack.Stack(api_key=api_key, access_token=delivery_token, environment=environment, config=config)
    return stack

def getEntries(contentType):
    '''
    Get all entries of some content type
    '''
    stack = initStack()
    response = stack.content_type(contentType).query().find()
    resArr = []
    if response:
        for res in response:
            resArr.append(res.json)
        return resArr
    return None

def getLandingPage(path):
    '''
    Simple method - gets landing_page from Contentstack based on URL field (path)
    '''
    res = search('landing_page', 'url', '/' + path)
    try:
        return res
    except Exception as e:
        print('\n\nError!\n\n', e)
        return None


def search(contentType, key, value):
    '''
    Searches for an entry based on content type and search term.
    '''
    stack = initStack()
    contentTypeInit = stack.content_type(contentType)
    query = contentTypeInit.query()
    query = query.where(key, value)
    res = query.find()
    if res:
        try:
            return res[0].json # Should only find a single entry
        except Exception as e:
            print('Error in content.search()', e)
    return None

def getEntry(contentType, uid):
    '''
    Fetches a single entry based on content type and uid
    '''
    stack = initStack()
    content_type = stack.content_type(contentType)
    entry = content_type.entry(uid)
    entry = entry.fetch()
    try:
        return entry.json
    except AttributeError: #JSON not available for some reason
        print('JSON not available in content.getEntry()')
        print(entry.error_message)
    return None

def findLPReferences(entry):
    '''
    Landing Page References - Contentype: Snippets
    '''
    refDict = {}
    print(entry)
    if 'reference_group' in entry: # If the landing_page has references
        for refGroup in entry['reference_group']:
            refTitle = refGroup['reference_title']
            if 'snippet_reference' in refGroup:
                refEntryArr = []
                for ref in refGroup['snippet_reference']:
                    refEntry = getEntry(ref['_content_type_uid'], ref['uid'])
                    if refEntry is not None:
                        refEntryArr.append(refEntry)
            refDict[refTitle] = refEntryArr
        return refDict
    return None

def constructHeaderMenu(header):
    '''
    Not a Contentstack thing, strictly speaking.
    Reconstructing the menu for the jinji templating machine.
    '''
    menu = {}
    for item in header:
        for key, value in item.items():
            if key == 'landing_page_item':
                entry = getEntry(value['reference'][0]['_content_type_uid'], value['reference'][0]['uid'])
                if entry['url'] == '/':
                    menu['Home'] = '/'
                else:
                    menu[entry['title']] = entry['url']
            elif key == 'custom_item':
                menu[value['label']] = value['path']
            elif key == 'external_item':
                menu[value['link']['title']] = value['link']['href']
            else:
                return None
    return menu
