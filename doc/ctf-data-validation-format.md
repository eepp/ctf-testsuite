CTF data validation format
==========================

This document describes the required format that a CTF reader must
output in order for the decoded binary data to be validated by the CTF
test suite.

The validation process goes like this:

  1. The test author writes:
     * a metadata file;
     * one or more CTF binary stream files; and
     * a validation file containing the expected values of this trace
       (an array of packet info and event objects; see below).
  2. The CTF reader under test is called to read those binary stream
     files, with the appropriate arguments to output the format
     specified here.
  3. The CTF reader output is compared to the validation file written
     by the test author, and warnings/errors are reported if there's
     any.


Format overview
---------------

The CTF data validation format is a specific schema of
[JSON](http://json.org/). The format is easy to write by hand, easy to
write by a given program using any JSON library/package, and easy to
parse by the CTF test suite.

The following objects are defined by this document:

  * Packet info
  * Event
  * Integer field
  * Floating point number field
  * Enumeration field
  * String field
  * Array field
  * Sequence field
  * Structure field

A _validation file_ is a JSON array of packet info and event objects.
A packet info object inserted in a validation file's array sets the
current packet information of the following event objects.

The event objects must be inserted _in order of timestamp_, with
appropriate clock offsets applied; this ensures a complete trace
validation. If two events occur at the exact same timestamp, the order
between them is not important.


Objects
-------

This section defines the schemas of all the JSON objects listed above.


### Packet info

Packet info objects set the current packet information of the following
event objects within a validation file.

A packet info object honors this schema:

```javascript
{
    "packet-header": /* packet header field object... */,
    "packet-context": /* packet context field object... */,
}
```

Any property of a packet info object must be a field object, or may be
absent if the packet doesn't have any such property. The packet info
object properties may also be set to `null` to skip their validation.


### Event

Event objects contain their header, stream event context, context, and
payload. They also contain their containing packet header and context.
An event object honors this schema:

```javascript
{
    "header": /* event header field object... */,
    "stream-context": /* stream event context field object... */,
    "context": /* event context field object... */,
    "payload": /* event payload field object... */
}
```

Any property of an event object must be a field object, or may be
absent if the event doesn't have any such property. The event object
properties may also be set to `null` to skip their validation.


### Integer field

An integer field object honors this schema:

```javascript
{
    "type": "integer",
    "value": /* VALUE */
}
```

where `VALUE` is a JSON integer number, e.g.:

```javascript
{
    "type": "integer",
    "value": -38291
}
```

Alternatively, an integer field object may be a simple JSON integer
number, e.g.:

```javascript
-38291
```


### Floating point number field

A floating point number field object honors this schema:

```javascript
{
    "type": "float",
    "value": /* VALUE */
}
```

where `VALUE` is a JSON number, e.g.:

```javascript
{
    "type": "float",
    "value": 3.1415926
}
```

Alternatively, a floating point number field object may be a simple JSON
number, e.g.:

```javascript
3.1415926
```


### Enumeration field

An enumeration field object honors this schema:

```javascript
{
    "type": "enum",
    "label": LABEL
}
```

where `LABEL` is the enumeration field's label (JSON string), e.g.:

```javascript
{
    "type": "enum",
    "label": "MY LABEL"
}
```


### String field

A string field object honors this schema:

```javascript
{
    "type": "string",
    "value": /* VALUE */
}
```

where `VALUE` is a JSON string, e.g.:

```javascript
{
    "type": "string",
    "value": "that's right man"
}
```

Alternatively, a string field object may be a simple JSON string, e.g.:

```javascript
"that's right man"
```


### Array field

An array field object honors this schema:

```javascript
{
    "type": "array",
    "elements": [
        // zero or more field objects...
    ]
}
```

Alternatively, an array field object may be a simple JSON array, e.g.:

```javascript
[
    // zero or more field objects...
]
```

An element may be `null` to skip its validation.


### Sequence field

A sequence field object honors this schema:

```javascript
{
    "type": "sequence",
    "elements": [
        // zero or more field objects...
    ]
}
```

Alternatively, a sequence field object may be a simple JSON array, e.g.:

```javascript
[
    // zero or more field objects...
]
```

An element may be `null` to skip its validation.


### Structure field

A structure field object honors this schema:

```javascript
{
    "type": "struct",
    "fields": {
        // zero or more fields
    }
}
```

Fields are properties of the `fields` JSON object, where the key
corresponds to the field name, and its value to the field value
(a field object), e.g.:

```javascript
{
    "type": "struct",
    "fields": {
        "my_field": 23,
        "other_field": {
            "type": "enum",
            "label": "STATE_INIT"
        }
    }
}
```

A field's value may be set to `null` to skip a field's validation, e.g.:

```javascript
{
    "type": "struct",
    "fields": {
        "my_field": 23,
        "other_field": null
    }
}
```


### Variant field?

Variant field objects do not exist because they would not carry anything
else than their selected field object. Thus, when a reader needs to
output a variant following this format, it must output the variant's
selected field directly instead.


Example
-------

Here's a complete example:

```javascript
[
    {
        "packet-header": {
            "type": "struct",
            "fields": {
                "magic": 3254525889,
                "uuid": [
                    83, 38, 114, 26, 229, 211, 136, 54,
                    112, 4, 5, 113, 98, 252, 51, 215
                ],
                "stream_id": 0
            }
        },
        "packet-context": {
            "type": "struct",
            "fields": {
                "timestamp_begin": 1431029082190941952,
                "timestamp_end": 1431029083075216594,
                "content_size": 991,
                "packet_size": 4096,
                "events_discarded": 1,
                "cpu_id": 2
            }
        }
    },
    {
        "header": {
            "type": "struct",
            "fields": {
                "id": 23,
                "timestamp": 1549948754
            }
        },
        "payload": {
            "type": "struct",
            "fields": {
                "_fd": 5,
                "_name": "my-attr",
                "_value": -1754,
                "_size": null,
                "_flags": 0
            }
        }
    },
    {
        "header": {
            "type": "struct",
            "fields": {
                "id": 12,
                "timestamp": 38149948754
            }
        },
        "payload": {
            "type": "struct",
            "fields": {
                "my_float": -17.34,
                "ip": [192, 168, 0, 102],
                "more_stuff": [23, 0, [1, null, 3], "a string", -17.34],
                "msg": {
                    "type": "struct",
                    "fields": {
                        "dst": 1944875,
                        "content": "get_apples"
                    }
                }
            }
        }
    }
]
```
