## Tiny URL 

### structure 
```
├── server.py
├── static
│   ├── html
│   │   └── main.html
│   └── js
│       └── query.js
└── util
    ├── __init__.py
    ├── app.py
    ├── config.py
    └── redis_singleton.py
```

### View
![image](https://user-images.githubusercontent.com/20620478/123072203-ea15dd00-d447-11eb-8d70-c7ffd32d69c6.png)

### Data Type 

##### Shorten Hash
```
127.0.0.1:6379> TYPE eff0a0
hash
127.0.0.1:6379> HGETALL eff0a0
 1) "url"
 2) "https://www.facebook.com"
 3) "created_at"
 4) "1624440102243"
 5) "session_id"
 6) "6fb663f8431843e393f41166120205fa"
 7) "timestamp"
 8) "1624440102"
 9) "last_viewed"
10) "1624440111"
11) "pageview"
12) "2"
127.0.0.1:6379> 
```
