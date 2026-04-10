import addressbook_pb2 as addr

person = addr.Person(
    name='alice',
    email='alice@gmail.com',
    phones=[
        addr.PhoneNumber(number='+375-29-12-12-123', type=addr.PHONE_TYPE_WORK)
    ]
)
print(person)

person_bytes = person.SerializeToString()
print(person_bytes)
print(person_bytes.hex(' '))
print(len(person_bytes))

# 00001 010 - 0a
# 00010 000 - 10
# 00011 010 - 1a
# 00100 010 - 22

print()

person_from_bytes = addr.Person.FromString(person_bytes)
print(person_from_bytes)

import json
person_data = {
    'name': 'alice',
    'id': 1,
    'email': 'alice@gmail.com',
    'phones': [
        {
            'number': '+375-29-12-12-123',
            'type': 3
        }
    ]
}
person_json = json.dumps(person_data, separators=(',', ':'))
print(person_json)
print(len(person_json))