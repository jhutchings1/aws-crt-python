# Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://aws.amazon.com/apache2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import _aws_crt_python
import aws_crt.io

def _default_on_connect(return_code, session_present):
    pass
def _default_on_disconnect(return_code):
    pass

class Will(object):
    __slots__ = ['topic', 'qos', 'payload', 'retain']

    def __init__(self, topic, qos, payload, retain):
        self.topic = topic
        self.qos = qos
        self.payload = payload
        self.retain = retain

class Client(object):
    __slots__ = ['_internal_connection', 'elg', 'client_id', 'username', 'password', 'will']

    def __init__(self, event_loop_group, client_id):

        assert isinstance(event_loop_group, aws_crt.io.EventLoopGroup)

        self.elg = event_loop_group
        self.client_id = client_id

        self.username = None
        self.password = None
        self.will = None

    def connect(self,
            host_name, port,
            ca_path, key_path, certificate_path,
            on_connect=_default_on_connect,
            on_disconnect=_default_on_disconnect,
            use_websocket=False, alpn=None,
            clean_session=True, keep_alive=0):

        assert use_websocket == False

        self._internal_connection = _aws_crt_python.mqtt_new_connection(
            self.elg._internal_elg,
            host_name,
            port,
            ca_path,
            key_path,
            certificate_path,
            alpn,
            self.client_id,
            keep_alive,
            on_connect,
            on_disconnect,
            )

        if self.will:
            _aws_crt_python.mqtt_set_will(self._internal_connection, self.will.topic, self.will.payload, self.will.qos, self.will.retain)

        if self.username:
            _aws_crt_python.mqtt_set_login(self._internal_connection, self.username, self.password)

    def set_will(self, topic, QoS, payload, retain=False):
        self.will = Will(topic, QoS, payload, retain)

    def set_login(self, username, password=None):
        self.username = username
        self.password = password

    def disconnect(self):
        return _aws_crt_python.mqtt_disconnect(self._internal_connection)

    def subscribe(self, topic, qos, callback, suback_callback=None):
        return _aws_crt_python.mqtt_subscribe(self._internal_connection, topic, qos, callback, suback_callback)

    def unsubscribe(self, topic, unsuback_callback=None):
        return _aws_crt_python.mqtt_unsubscribe(self._internal_connection, topic, unsuback_callback)

    def publish(self, topic, payload, qos, retain=False, puback_callback=None):
        _aws_crt_python.mqtt_publish(self._internal_connection, topic, payload, qos, retain, puback_callback)