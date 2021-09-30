
# clients for db-api   

Any HTTP client will work.  

The API follows the Representational state transfer (REST) architecture and standards.  Database methods and REST calls are correlated with the standard HTTP methods GET, POST, PUT, PATCH, DELETE.  All API responses are in JSON.  Additionally, HTTP basic authentication is required for all requests.  

Initially the API only accepted JSON (application/json), but since 1.0.2 also accepts Form POST (application/x-www-form-urlencoded) data.  Sending JSON data with HTTP Basic Auth is perhaps not as trivial as it may seem, depending on your programming language or tool.  

A REST client will do best.

---   
  
https://en.wikipedia.org/wiki/Representational_state_transfer    
https://en.wikipedia.org/wiki/Database   
https://en.wikipedia.org/wiki/API   
https://en.wikipedia.org/wiki/JSON    
https://en.wikipedia.org/wiki/Basic_access_authentication    
https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods    

https://en.wikipedia.org/wiki/MariaDB    
https://en.wikipedia.org/wiki/Patch_verb    

"REST API Design Rulebook"  https://www.oreilly.com/library/view/rest-api-design/9781449317904/    


