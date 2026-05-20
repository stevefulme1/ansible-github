#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: organization_hook
short_description: Manage orgs
version_added: "1.0.0"
description:
  - Create, update, and delete organization_hook resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the organization_hook resource.
    type: str
    choices: ['present', 'absent']
    default: present

  active:
    description:
      - >-
        Determines if notifications are sent when the webhook is triggered. Set to true to send notifications.
    type: bool

    default: true

  config:
    description:
      - >-
        Key/value pairs to provide settings for this webhook.
    type: dict

  events:
    description:
      - >-
        Determines what events the hook is triggered for.
    type: list
    elements: str

    default: ["push"]

  name:
    description:
      - >-

    type: str

extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""
- name: Create a organization_hook
  stevefulme1.github.organization_hook:

    state: present
  # API: POST /orgs/{org}/hooks

- name: Update a organization_hook
  stevefulme1.github.organization_hook:
    id: "existing_id"

    active: "updated_active"

    config: "updated_config"

    events: "updated_events"

    name: "updated_name"

    state: present
  # API:

- name: Delete a organization_hook
  stevefulme1.github.organization_hook:
    id: "existing_id"
    state: absent
  # API: DELETE /orgs/{org}/hooks/{hook_id}
"""

RETURN = r"""
id:
  description: >-

  returned: success
  type: int

url:
  description: >-

  returned: success
  type: str

ping_url:
  description: >-

  returned: success
  type: str

deliveries_url:
  description: >-

  returned: success
  type: str

name:
  description: >-

  returned: success
  type: str

events:
  description: >-

  returned: success
  type: list

active:
  description: >-

  returned: success
  type: bool

config:
  description: >-

  returned: success
  type: dict

updated_at:
  description: >-

  returned: success
  type: str

created_at:
  description: >-

  returned: success
  type: str

type:
  description: >-

  returned: success
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.github.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def get_current_state(client, module):
    """Retrieve the current state of the organization_hook via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    name = module.params.get("name")
    search_key = "name"
    search_value = name if identifier is None else identifier

    if search_value is None:
        return None
    try:
        items = client.get("/orgs/{org}/hooks")
        if isinstance(items, dict):
            items = items.get("results", items.get("data", items.get("items", [])))
        for item in items:
            if str(item.get(search_key)) == str(search_value):
                return item
            if str(item.get("id")) == str(search_value):
                return item
        return None
    except ClientError:
        return None


def needs_update(current, desired):
    """Compare current state against desired params and return True if an update is needed."""
    if current is None:
        return True
    for key, value in desired.items():
        if value is None:
            continue
        current_value = current.get(key)
        if current_value != value:
            return True
    return False


def build_payload(module):
    """Build the API request payload from module params."""
    payload = {}

    if module.params.get("active") is not None:
        payload["active"] = module.params["active"]

    if module.params.get("config") is not None:
        payload["config"] = module.params["config"]

    if module.params.get("events") is not None:
        payload["events"] = module.params["events"]

    if module.params.get("name") is not None:
        payload["name"] = module.params["name"]

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),

            active=dict(
                type="bool",

                default=True,

            ),

            config=dict(
                type="dict",

            ),

            events=dict(
                type="list",
                elements="str",

                default=["push"],

            ),

            name=dict(
                type="str",

            ),

        )
    )

    module = AnsibleModule(
        argument_spec=spec,
        supports_check_mode=True,

    )

    state = module.params["state"]
    result = dict(changed=False, diff=dict(before={}, after={}))

    try:
        client = Client(module)
        current = get_current_state(client, module)

        if state == "present":
            desired = build_payload(module)

            if current is None:
                # Resource does not exist — create it
                result["changed"] = True
                result["diff"]["before"] = {}
                result["diff"]["after"] = desired

                if not module.check_mode:

                    response = client.POST(
                        "/orgs/{org}/hooks",
                        data=desired,
                    )
                    result.update(response if isinstance(response, dict) else {})

            elif needs_update(current, desired):
                # Resource exists but needs updating
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = dict(current, **{k: v for k, v in desired.items() if v is not None})

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "".replace(
                        "{id}", str(identifier)
                    )
                    response = client.put(
                        path,
                        data=desired,
                    )
                    result.update(response if isinstance(response, dict) else {})

            else:
                # Resource exists and is up-to-date

                result["id"] = current.get("id")

                result["url"] = current.get("url")

                result["ping_url"] = current.get("ping_url")

                result["deliveries_url"] = current.get("deliveries_url")

                result["name"] = current.get("name")

                result["events"] = current.get("events")

                result["active"] = current.get("active")

                result["config"] = current.get("config")

                result["updated_at"] = current.get("updated_at")

                result["created_at"] = current.get("created_at")

                result["type"] = current.get("type")

        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/orgs/{org}/hooks/{hook_id}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
