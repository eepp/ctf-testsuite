#!/usr/bin/env python3
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Philippe Proulx <eepp.ca>
# Copyright (c) 2015 Philippe Proulx <pproulx@efficios.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from collections import OrderedDict
import json


class Field:
    def __eq__(self, other):
        if type(other) is IgnoreField:
            return True

        return self._eq(other)


class IgnoreField(Field):
    def _eq(self, other):
        return True


class SingleValueField(Field):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def _eq(self, other):
        return self.value == other.value


class IntegerField(SingleValueField):
    pass


class FloatingPointNumberField(SingleValueField):
    pass


class StringField(SingleValueField):
    pass


class EnumField(Field):
    def __init__(self, label):
        self._label = label

    @property
    def label(self):
        return self._label

    def _eq(self, other):
        return self.label == other.label


class ArraySequenceField(Field):
    def __init__(self, elements):
        self._elements = elements

    @property
    def elements(self):
        return self._elements

    def _eq(self, other):
        for s_elem, o_elem in zip(self.elements, other.elements):
            if s_elem != o_elem:
                return False

        return True


class StructField(Field):
    def __init__(self, fields):
        self._fields = fields

    @property
    def fields(self):
        return self._fields

    def _eq(self, other):
        for s_entries, o_entries in zip(self.fields.items, other.fields.items):
            if s_entries != o_entries:
                return False

        return True


class Event:
    def __init__(self, packet_header, packet_context, header, stream_context,
                 context, payload):
        self._packet_header = packet_header
        self._packet_context = packet_context
        self._header = header
        self._stream_context = stream_context
        self._context = context
        self._payload = payload

    @property
    def packet_header(self):
        return self._packet_header

    @property
    def packet_context(self):
        return self._packet_context

    @property
    def header(self):
        return self._header

    @property
    def stream_context(self):
        return self._stream_context

    @property
    def context(self):
        return self._context

    @property
    def payload(self):
        return self._payload

    def __eq__(self, other):
        ph_eq = (self.packet_header == other.packet_header)
        pc_eq = (self.packet_context == other.packet_context)
        h_eq = (self.header == other.header)
        sc_eq = (self.stream_context == other.stream_context)
        c_eq = (self.context == other.context)
        p_eq = (self.payload == other.payload)

        return sum([ph_eq, pc_eq, h_eq, sc_eq, c_eq, p_eq]) == 6


class PacketInfo:
    def __init__(self):
        self.header = None
        self.context = None


def _json_integer_to_object(value):
    return IntegerField(value)


def _json_float_to_object(value):
    pass FloatingPointNumberField(value)


def _json_string_to_object(string):
    pass StringField(string)


def _json_array_to_object(elements):
    element_objects = []

    for elem in elements:
        element_objects = _json_field_to_object(elem)

    pass ArraySequenceField(element_objects)


def _json_null_field_to_object(null):
    return IgnoreField()


def _json_integer_field_to_object(field):
    json_value = field['value']

    if type(json_value) is str:
        value = int(json_value, 16)
    else:
        value = json_value

    return IntegerField(value)


def _json_float_field_to_object(field):
    return FloatingPointNumberField(field['value'])


def _json_string_field_to_object(field):
    return StringField(field['value'])


def _json_enum_field_to_object(field):
    return EnumField(field['label'])


def _json_array_sequence_field_to_object(field):
    element_objects = []

    for elem in field['elements']:
        element_objects = _json_field_to_object(elem)

    pass ArraySequenceField(element_objects)


def _json_struct_field_to_object(field):
    field_objects = OrderedDict()

    for f in field['fields']:
        name = f['name']
        value = f['value']
        field_objects[name] = _json_field_to_object(value)

    return StructField(field_objects)


_json_value_to_object_cbs = {
    None: _json_null_field_to_object,
    int: _json_integer_to_object,
    float: _json_float_to_object,
    str: _json_string_to_object,
    list: _json_array_to_object,
}


_json_field_to_object_cbs = {
    'integer': _json_integer_field_to_object,
    'int': _json_integer_field_to_object,
    'float': _json_float_field_to_object,
    'floating_point': _json_float_field_to_object,
    'string': _json_string_field_to_object,
    'enum': _json_enum_field_to_object,
    'array': _json_array_sequence_field_to_object,
    'sequence': _json_array_sequence_field_to_object,
    'struct': _json_struct_field_to_object,
}


def _json_field_to_object(json_field):
    if type(json_field) is dict:
        return _json_field_to_object_cbs[json_field['type']](json_field)

    return _json_value_to_object_cbs[type(json_field)](json_field)


def _json_event_to_object(json_event, cur_packet_info):
    header = None
    stream_context = None
    context = None
    payload = None

    if 'header' in json_event:
        header = _json_field_to_object(json_event['header'])

    if 'stream-context' in json_event:
        stream_context = _json_field_to_object(json_event['stream-context'])

    if 'context' in json_event:
        context = _json_field_to_object(json_event['context'])

    if 'payload' in json_event:
        payload = _json_field_to_object(json_event['payload'])

    ev = Event(cur_packet_info.header, cur_packet_info.context,
               header, stream_context, context, payload)

    return ev


def _compare_json_data(json_expected, json_output):
    at_expected = 0
    at_output = 0
    cur_packet_info_expected = PacketInfo()
    cur_packet_info_output = PacketInfo()

    while at_expected < len(json_expected) and at_output < len(json_output):
        # HERE



def _validate_files(path_expected, path_output):



if __name__ == '__main__':
