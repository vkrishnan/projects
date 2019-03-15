'''
Created on 21 Jan, 2016
@author: Rahul Verma
'''
def uncheck_dependency_comp(self, fpath):
    """
    This functions take the source.html file of the review page
    and parse it to find the component having dependency.

    It will create a list having id of the component having
    dependency and will return that list to the calling keyword.

    Example:
    | Uncheck Dependency Comp | source.html |
    """
    soup = BeautifulSoup(open(fpath).read(), "lxml")
    table = soup.findAll('table')
    table_rows = table[2].findAll('tr')
    c_id = []
    for row in table_rows:
        try:
            if row.span.string == 'error':
                c = row.a['id']
                c_id.append(c)
        except:
            continue
    return c_id
