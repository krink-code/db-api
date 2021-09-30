
# Java has java.net.HttpURLConnection

```
import java.net.URL;
import java.net.HttpURLConnection;
```

```
        URL url = new URL("http://127.0.0.1:8980/api");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setRequestProperty("Accept", "application/json");
        conn.setRequestProperty("Authorization", "Basic " + base64);
```

---  

# Example java

javac ShowDataBases.java
java ShowDataBases


```
$ java ShowDataBases 
Output from Server .... 

[
  [
    "information_schema"
  ], 
  [
    "example"
  ], 
  [
    "test"
  ]
]
```

