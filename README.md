# quotr README

## Change Log

### 2021-04-15

- Updated quotes/routes.py to grab all authors (sorted) and send them to the new quote template.

- Changed the autocompelte script to take the authors list from flask, put it into an array, and use that array to supply the autocomplete. This keeps the page (ajax) from hitting the '/author/_autocomplete' route.

- Removed below javascript from post.html but left the routes (commented out).

```javascript
<!-- AUTHORS FLASK API CALL -->
<script>
  $(function () {
    $.ajax({
      url: '{{ url_for("quotes_bp.author_autocomplete") }}'
    }).done(function (data) {
      $('#author').autocomplete({
        source: data,
        minLength: 2
      });
    });
  });
</script>
```

### 2021-04-21

- fixed the mispelling of "widsom" in the sample quotes file.
- reset both dev and production databases
- added query for prefilled "uncategorized" category on new quote page in quotes/routes.py

```python
# pre-select the uncategorized category as a default
uncategorized_category_id = Category.query.filter_by(name='uncategorized').first().id
form.category.data = uncategorized_category_id
```

- updated autocomplete jqery to 'https'

### 2021-04-22

- added flask-migrate  
- updated requirements.txt  
- reset database  
- fixed update quote bug (category dropdown for update quote using same function from 4/21)  
- updated email body from share modal to include new line and uri encode it... works on Gmail, not sure about others.  

```javascript
var email_body = 'Hey, I found this quote and thought you might like it!\n\n' +
    '"' + quote_text + '"\n\n' +
    'View it online: ' + quote_link;

var email_link = encodeURI("mailto:?subject=Check out this quote!&body=" + email_body);
```

### 2021-04-24

Setup basic [full text search indexing](https://bart.degoe.de/building-a-full-text-search-engine-150-lines-of-code/). Can be found in quotes/search.py.

- installed [PyStemmer] to help with search tokens  
- builds an entire index before first request  


[PyStemmer]: https://github.com/snowballstem/pystemmer

```python
@main_bp.before_app_first_request
def before_app_first_request():
    quotes = Quote.query.all()
    search = Search()
    search.index_tokens(quotes)
```

- author name also added to tokens

```python
# add author name to tokens
tokens.extend(analyze(quote.author.name))
```

- delete tokens or quote references (quote.id) when a quote is deleted from the db

```python
def remove_deleted_quote_tokens(self, quote):
    self.quote = quote
    tokens = analyze(self.quote.content)
    # add author name to tokens
    tokens.extend(analyze(quote.author.name))
    # remove tokens from index
    for token in tokens:
        # if token only has one quote ref then delete it
        if len(self.index[token]) == 1:
            del self.index[token]
        else:
            # if token has multiple quote refs then just delete ref
            if token in self.index:
                self.index[token].remove(self.quote.id)
```

- on quote update, remove all tokens no matter the change, then resubmit all tokens for the updated quote  
- on quote update, remove previous author if they no longer have any quotes

### 2021-04-27

- removed user-select-all from index and quote page (annoying)
- removed quotation marks from all pages that didn't show a single quote
- added appropriate icons at top for each listing page
- built out search page
- added most loved quotes link to search page (limited to 10)
- added most love authors link to search page (limited to 10)
    - couldn't figure out a sqlalchemy query to get the result I was looking for so I just wrote a function in python to iterate over all of the authors and their quotes and add up their loves

```python
authors = Author.query.all()

loves_count = {}

for author in authors:
    # skip over author "Unknown" since it skews the results
    if author.name == 'Unknown':
        continue
    for quote in author.quotes:
        if quote.author.name not in loves_count:
            loves_count[quote.author.name] = 0
        loves_count[quote.author.name] += quote.loves_count

sorted_authors = sorted(loves_count.items(),
                        key=lambda item: item[1], reverse=True)
```

- built out search results listing page
- added javascript highlighting to the search tokens on the search results page
- added Token model to db to capture successfull search tokens

### 2021-04-27

- added most searched terms route
- term/token/tag cloud for top 100 search terms
- reset db migration to fresh start
- reset prod db to a fresh install
- pushed to prod server
- minor css tweaks
- restructured app layout
    - sep'd out authors and search into their own modules with a blueprint
    - put Search class into search.utils
    - cleaned up imports for all routes files

### 2021-05-05

- removed excess code from code from search route
- added in found_tokens function to return found Stemmer base tokens so that I can add those to the searched tokens db
- changed javascript to regex to match any words starting with the Stemmer base token => that matched entire word that's

```regex
/(?=\bthat['-]?)([a-zA-Z'-]+)/gi
```

## To-do's

- [ ] db sorting options
- [ ] db quote updated date
- [ ] db profile updates date
- [x] animated gif processor
- [x] csv importer for initial base quotes
- [x] random date generator for sample quotes
- [x] implement username urls instead of user id's
- [x] implement author name urls instead of author id's
- [x] change password reset email signature to 'quotr'
- [ ] continuious scrolling, lazy loading
- [ ] better buttons
- [ ] share actual quote content to facebook, not just the link
- [x] share actual quote content to email, not just the link
- [ ] check email body on differnet devices (mail, outlook, etc.)
- [x] remove author on quote delete if they have no other quotes
- [x] figure out how to remove authors if no more quotes after an update to a quote
- [x] add tokens on quote addition
- [x] remove tokens on quote deletion
- [x] add tokens on search update
- [x] figure out how to remove old tokens on search update
- [ ] add category count
- [x] add block for search terms that should show in top 100