
# JavaScript clients for db-api   

javascript client can simply use native fetch   
https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch  

```  
fetch('http://127.0.0.1:8980/api', {
    method: 'GET',
    headers: { Authorization: 'Basic ' + base64 }
})
    .then(response => response.json())
    .then(json => document.write(json))
    .catch(err => document.write('Request Failed ', err));
```  

use from source repo  

```  
<script src="https://gitlab.com/krink/db-api-server/-/raw/master/clients/JavaScript/js/db-api.js"  
        crossorigin="anonymous">  
</script>  
```  

