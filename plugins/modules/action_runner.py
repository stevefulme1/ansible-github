#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: action_runner
short_description: Manage actions
version_added: "1.0.0"
description:
  - Create, update, and delete action_runner resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the action_runner resource.
    type: str
    choices: ['present', 'absent']
    default: present

extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""
- name: Update a action_runner
  stevefulme1.github.action_runner:
    id: "existing_id"

    state: present
  # API:

- name: Delete a action_runner
  stevefulme1.github.action_runner:
    id: "existing_id"
    state: absent
  # API: DELETE /repos/{owner}/{repo}/actions/runners/{runner_id}
"""

RETURN = r"""
id:
  description: >-
    The ID of the runner.
  returned: success
  type: int

runner_group_id:
  description: >-
    The ID of the runner group.
  returned: success
  type: int

name:
  description: >-
    The name of the runner.
  returned: success
  type: str

os:
  description: >-
    The Operating System of the runner.
  returned: success
  type: str

status:
  description: >-
    The status of the runner.
  returned: success
  type: str

busy:
  description: >-

  returned: success
  type: bool

labels:
  description: >-

  returned: success
  type: list

ephemeral:
  description: >-

  returned: success
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.github.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def get_current_state(client, module):
    """Retrieve the current state of the action_runner via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    name = module.params.get("name")
    search_key = "name"
    search_value = name if identifier is None else identifier

    if search_value is None:
        return None
    try:
        items = client.get("/repos/{owner}/{repo}/actions/runners")
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

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),

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

                    pass


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

                result["runner_group_id"] = current.get("runner_group_id")

                result["name"] = current.get("name")

                result["os"] = current.get("os")

                result["status"] = current.get("status")

                result["busy"] = current.get("busy")

                result["labels"] = current.get("labels")

                result["ephemeral"] = current.get("ephemeral")


        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/repos/{owner}/{repo}/actions/runners/{runner_id}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)


    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
