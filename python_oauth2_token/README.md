Python Oauth2 Token Fetcher
==========================
Built for the Narrative API.

## Usage

After importing it in the project, the following should grant you a token

```python
from python_oauth2 import get_token

def do_token_stuff(token):
  print token

get_token('<client-id>', '<client-secret>', do_token_stuff)
```
