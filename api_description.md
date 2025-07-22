data

GET
​/v1​/data​/{metaType}
fetch metaType

Fetch game data by metaType
Parameters
Try it out
Name Description
x-api-key
string
(header)
auth api key from dev portal
metaType *
string
(path)
Meta Type, use 'hash' to find all types

Responses
Response content type

application/json
Code Description
200
200 response
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
GET
​/v1​/freeCharacters​/{matchingMode}
fetch freeCharacters by matchingMode

fetch freeCharacters by matchingMode
Parameters
Try it out
Name Description
x-api-key
string
(header)
auth api key from dev portal
matchingMode *
string
(path)
matchingMode (2: Normal, 3: Rank)

Responses
Response content type

application/json
Code Description
200
200 response
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
GET
​/v1​/l10n​/{language}
fetch l10n

Fetch l10n data by language
Parameters
Try it out
Name Description
x-api-key
string
(header)
auth api key from dev portal
language *
string
(path)
Korean, English, Japanese, ChineseSimplified, ChineseTraditional, French, Spanish, SpanishLatin, Portuguese, PortugueseLatin, Indonesian, German, Russian, Thai, Vietnamese

Responses
Response content type

application/json
Code Description
200
200 response
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
GET
​/v2​/data​/{metaType}
fetch metaType

Fetch game data by metaType
Parameters
Try it out
Name Description
x-api-key
string
(header)
auth api key from dev portal
metaType *
string
(path)
Meta Type, use 'hash' to find all types

Responses
Response content type

application/json
Code Description
200
200 response
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
default

OPTIONS
​/v1​/data​/{metaType}
Parameters
Try it out
Name Description
metaType *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/freeCharacters​/{matchingMode}
Parameters
Try it out
Name Description
matchingMode *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/games​/{gameId}
Parameters
Try it out
Name Description
gameId *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/l10n​/{language}
Parameters
Try it out
Name Description
language *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/rank​/top​/{seasonId}​/{matchingTeamMode}
Parameters
Try it out
Name Description
seasonId *
string
(path)
matchingTeamMode *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/rank​/top​/{seasonId}​/{matchingTeamMode}​/{serverCode}
Parameters
Try it out
Name Description
seasonId *
string
(path)
matchingTeamMode *
string
(path)
serverCode *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/rank​/{userNum}​/{seasonId}​/{matchingTeamMode}
Parameters
Try it out
Name Description
userNum *
string
(path)
seasonId *
string
(path)
matchingTeamMode *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/unionTeam​/{userNum}​/{seasonId}
Parameters
Try it out
Name Description
userNum *
string
(path)
seasonId *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/user​/games​/{userNum}
Parameters
Try it out
Name Description
userNum *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/user​/nickname
Parameters
Try it out
No parameters

Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/user​/stats​/{userNum}​/{seasonId}
Parameters
Try it out
Name Description
userNum *
string
(path)
seasonId *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/weaponRoutes​/recommend
Parameters
Try it out
No parameters

Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v1​/weaponRoutes​/recommend​/{routeId}
Parameters
Try it out
Name Description
routeId *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v2​/data​/{metaType}
Parameters
Try it out
Name Description
metaType *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string
OPTIONS
​/v2​/user​/stats​/{userNum}​/{seasonId}​/{matchingMode}
Parameters
Try it out
Name Description
userNum *
string
(path)
seasonId *
string
(path)
matchingMode *
string
(path)
Responses
Response content type

application/json
Code Description
200
200 response
Headers:
Name Description Type
Access-Control-Allow-Origin string
Access-Control-Allow-Methods string
Access-Control-Allow-Headers string


games

GET
​/v1​/games​/{gameId}
fetch game

rank/top

GET
​/v1​/rank​/top​/{seasonId}​/{matchingTeamMode}
fetch seasons' top rankers

GET
​/v1​/rank​/top​/{seasonId}​/{matchingTeamMode}​/{serverCode}
fetch seasons' top server rankers

fetch rankders by seasonId, matchingTeamMode, serverCode

Parameters
Try it out
Name Description
matchingTeamMode *
string
(path)
matching Team Mode (1,2,3)

seasonId *
string
(path)
season id (for ranking league) / 0 (for normal league)

x-api-key
string
(header)
auth api key from dev portal
serverCode *
string
(path)
server code
Responses
Response content type

application/json
Code Description
200
200 response
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
rank/user

GET
​/v1​/rank​/{userNum}​/{seasonId}​/{matchingTeamMode}
fetch user rank

fetch user rank by seasonId, matchingTeamMode

Parameters
Try it out
Name Description
matchingTeamMode *
string
(path)
matching Team Mode (1,2,3)

seasonId *
string
(path)
season id (for ranking league) / 0 (for normal league)

userNum *
string
(path)
user number
x-api-key
string
(header)
auth api key from dev portal
Responses
Response content type

application/json
Code Description
200
200 response
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
union/teams

GET
​/v1​/unionTeam​/{userNum}​/{seasonId}
fetch union rumble teams

user/games

GET
​/v1​/user​/games​/{userNum}
fetch user' games

fetch games by userNum
Parameters
Try it out
Name Description
userNum *
string
(path)
user number
x-api-key
string
(header)
auth api key from dev portal
next
string
(query)
paging parameter 'next' from previous response

Responses
Response content type

application/json
Code Description
200
200 response
Example Value
Model
{
"next": 0,
"code": 0,
"userGames": [
{
"userNum": 0,
"nickname": "string",
"masteryLevel": {}
}
],
"message": "string"
}
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
user/nickname

GET
​/v1​/user​/nickname
fetch user by nickname

fetch user by nickname
Parameters
Try it out
Name Description
x-api-key
string
(header)
auth api key from dev portal
query *
string
(query)
Responses
Response content type

application/json
Code Description
200
200 response
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
user/stats

GET
​/v1​/user​/stats​/{userNum}​/{seasonId}
fetch user' stats

fetch stats by userNum and seasonId
Parameters
Try it out
Name Description
seasonId *
string
(path)
season id (for ranking league) / 0 (for normal league)

userNum *
string
(path)
user number
x-api-key
string
(header)
auth api key from dev portal
Responses
Response content type

application/json
Code Description
200
200 response
Example Value
Model
{
"code": 0,
"message": "string"
}
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
GET
​/v2​/user​/stats​/{userNum}​/{seasonId}​/{matchingMode}
fetch user' stats

fetch stats by userNum and seasonId and matchingMode
Parameters
Try it out
Name Description
seasonId *
string
(path)
season id (for ranking league) / 0 (for normal league)

userNum *
string
(path)
user number
matchingMode *
string
(path)
matchingMode (2: Normal, 3: Rank)

x-api-key
string
(header)
auth api key from dev portal
Responses
Response content type

application/json
Code Description
200
200 response
Example Value
Model
{
"code": 0,
"message": "string"
}
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
weaponRoutes/recommend

GET
​/v1​/weaponRoutes​/recommend
fetch recommend weaponRoutes

Fetch recommend weaponRoutes
Parameters
Try it out
Name Description
x-api-key
string
(header)
auth api key from dev portal
next
string
(query)
paging parameter 'next' from previous response

Responses
Response content type

application/json
Code Description
200
200 response
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
GET
​/v1​/weaponRoutes​/recommend​/{routeId}
find recommend weaponRoute by route id

find recommend weaponRoute by route id
Parameters
Try it out
Name Description
x-api-key
string
(header)
auth api key from dev portal
routeId *
string
(path)
route id
Responses
Response content type

application/json
Code Description
200
200 response
404
404 response
Example Value
Model
{
"code": 0,
"message": "string"
}
429
429 response
Example Value
Model
{
"code": 0,
"message": "string"
}
