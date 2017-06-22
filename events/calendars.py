calIds = [
    'tgh4uc5t6uhr4icjrcgqfhe18r2uu3fg@import.calendar.google.com',
    '11j5qfhbb916srru7kuae99i4rn3p8r5@import.calendar.google.com',
    '89aheia1si29mqt1kvuprggnid983m87@import.calendar.google.com',
    'sv5rg9q32cg6qhabdgi33fjur45vcilh@import.calendar.google.com',
    '3drnie5h5b5mr73acgcqpvvc2k@group.calendar.google.com',
    'torontojs.com_o83mhhuck726m114hgkk3hl79g@group.calendar.google.com',
    '59s1qmiqr7bo98uqkek5ba7er2eduk3t@import.calendar.google.com',
    'k6l8oiu416ftcjpjetn0r7a79me8pq4r@import.calendar.google.com',
    'h1tmhrt7ruckpk3ad20jaq55amvaiubu@import.calendar.google.com',
    '7i14k13k6h3a9opbokgmj63k1074gd78@import.calendar.google.com',
    'cmm8uhv8s34d21711h5faa4e3a34napd@import.calendar.google.com',
    '3usg04moak5e7qejj73mu9u05p2r3rer@import.calendar.google.com'
]
url_format = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events?singleEvents=true&key=AIzaSyA-xW0xIfYvro-zD0JCLRfJwqs6s2MmKmU"
endpoints = [(calId, url_format.format(calendar_id=calId)) for calId in calIds]
