<meta name="google-site-verification" content="2yt4i3kLYL6SmmbYdvnQsT8wPgBng9mcFI4zP9GMO8M" />

# code was largely taken from https://github.com/deadly/valorant-stream-yoinker deadly, only added some cool stuff now that streamer yoinker is broken :3

# valorant public record

valorant public record resolves the hidden usernames of players cowering behind streamer mode by interrogation of multiple local riot client endpoints in real time. these resolved identities are committed to a local cache; should you find them in a subsequent match, their username will be revealed even if hidden in your live match. the post match final scoreboard is used to retroactively update the log. panzis who use streamer mode and don't stream are cringe. it also tells you who is qued with who and pastes tracker.gg links to each individual in the lobby in cmd.

# in the future i may add something to store all ids in a massive database online that will match hidden user ids to tracker.gg links if enough data is collected through people using the program

# how to use

make sure valorant is open before running

first edit player.py and add your username (just the username not the tag) so you don't log yourself consistently, then edit settings.json and enter your region. type in one of these within the quotations in settings.json: NA, EU, LATAM, BR, AP, KR.

<img width="904" height="247" alt="image" src="https://github.com/user-attachments/assets/cee7d949-cf08-4fd9-b45a-568dfc3afaaf" />

open cmd and type "cd [path where files extracted]", press enter, then type "python main.py"

when scan is finished either type "twitch" to scan for twitch usernames or wait until the match ends and type "done" to log revealed players into cache and overwrite hidden players in cache/identity log

# there is a chance you can reveal someone live during a match but its luck based. manually looking at the [party] seeing who is qued with who and if one of them has streamer mode on and the other doesn't can easily be done by copying and pasting the tracker link from the program

# examples

initial scan

<img width="572" height="999" alt="image" src="https://github.com/user-attachments/assets/e5270bb2-fe29-4744-aeb2-d903ef269124" />


scan done (type done when match is over)

<img width="837" height="255" alt="image" src="https://github.com/user-attachments/assets/3ca17e58-8f06-4f27-9324-08f9ba676819" />


twitch

<img width="653" height="84" alt="image" src="https://github.com/user-attachments/assets/ca443c97-21d8-45f3-865f-a972d81c253b" />


example of revealed player (revealed meaning hidden username player not twitch username) during live match

<img width="703" height="384" alt="image" src="https://github.com/user-attachments/assets/b439436e-384d-4f7d-9594-50f54139d695" />


if a user is in a future match of yours with this program open you will be able to reveal them because of the cache

# viewing the cache

open cmd and type in cd [directory where session_viewer.py is located] and then type python session_viewer.py

example of viewing each person logged per session:

<img width="741" height="603" alt="image" src="https://github.com/user-attachments/assets/786db23e-2461-4910-bc9f-f0c7e8cdfec9" />

# can this get me banned

use at own risk, only one documented "high level" case of a tier 2/3 pro player getting perma banned using the code this project was iterated from. 

he was given a temporary suspension instead by itsgamerdoc and perma was reversed

# faq

question: does this spam api calls to riot's api: 

answer: when you are out of agent select and all possible names are logged, hidden or not, the api calls stop. 

question: i need help installing 

answer: use search engine and type "how to install python & run code from github" 

question: why make this program if people wanna stay private

answer: streamer mode is cringe for people who dont stream 

![bobby-shmurda-money-dance](https://github.com/user-attachments/assets/f7b45504-77e6-4bdb-b55e-03911463fda1)


# license

Copyright (c) 2026 DextroAmph89
Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
