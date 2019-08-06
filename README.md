# miniter
> <깔끔한 파이썬 탄탄한 백엔드> 실습 - flask 미니 트위터 api 개발

#### 기능
* [회원가입](#회원가입)
* [로그인](#로그인)
* [트윗](#300자-제한-트윗-올리기)
* [다른 회원 팔로우 하기](#팔로우)
* [다른 회원 언팔로우 하기](#언팔로우)
* [타임라인](#타임라인)

<br>

### 회원가입
##### request

```http
POST /sign-up HTTP/1.1
Content-Type: application/json
{
	"email":"209rrsz@gmail.com",
	"name":"jian",
	"password":"test1234",
	"profile":"study flask"
}
```

##### response

```http
HTTP/1.1 200 OK
content-type: application/json
{
    "email": "209rrsz@gmail.com",
    "id": 1,
    "name": "jian",
    "password": "test1234",
    "profile": "study flask"
}
```

<br>

### 로그인
##### request

```http
POST /login HTTP/1.1
Content-Type: application/json
{
	"email":"209rrsz@gmail.com",
	"password":"test1234"
}
```

##### response

```http
HTTP/1.1 200 OK
content-type: application/json
{
    "access_token": "ESDFsdijfhw@34235dsafdDSFsd3......."
}
```

<br>

### 300자 제한 트윗 올리기
##### request

```http
POST /tweet HTTP/1.1
Content-Type: application/json
{
	"id":1,
	"tweet":"hello, world"
}
```

##### response

```http
HTTP/1.1 200 OK
content-type: application/json
```

<br>

### 팔로우
##### request

```http
POST /follow HTTP/1.1
Content-Type: application/json
{
	"id": 1,
	"follow": 2
}
```

##### response

```http
HTTP/1.1 200 OK
```


<br>

### 언팔로우
##### request

```http
POST /unfollow HTTP/1.1
Content-Type: application/json
{
	"id": 1,
	"unfollow": 2
}
```

##### response

```http
HTTP/1.1 200 OK
```

<br>

### 타임라인
##### request

```http
GET /timeline/1 HTTP/1.1
```

##### response

```http
HTTP/1.1 200 OK
content-type: application/json
{
    "timeline": [
        {
            "tweet": "nice to meet you!",
            "user_id": 2
        },
        {
            "tweet": "hello, world",
            "user_id": 1
        }
    ],
    "user_id": 1
}
```
