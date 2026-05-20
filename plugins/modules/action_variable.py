#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: action_variable
short_description: Manage actions
version_added: "1.0.0"
description:
  - Create, update, and delete action_variable resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the action_variable resource.
    type: str
    choices: ['present', 'absent']
    default: present

  name:
    description:
      - >-
        The name of the variable.
    type: str

  selected_repository_ids:
    description:
      - >-
        An array of repository ids that can access the organization variable. You can only provide a...
    type: list

  value:
    description:
      - >-
        The value of the variable.
    type: str

  visibility:
    description:
      - >-
        The type of repositories in the organization that can access the variable. selected means only...
    type: str

    choices: ["all", "private", "selected"]

extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""
- name: Create a action_variable
  stevefulme1.github.action_variable:

    state: present
  # API: POST /repos/{owner}/{repo}/actions/variables

- name: Update a action_variable
  stevefulme1.github.action_variable:
    id: "existing_id"

    name: "updated_name"

    selected_repository_ids: "updated_selected_repository_ids"

    value: "updated_value"

    visibility: "updated_visibility"

    state: present
  # API:

- name: Delete a action_variable
  stevefulme1.github.action_variable:
    id: "existing_id"
    state: absent
  # API: DELETE /repos/{owner}/{repo}/actions/variables/{name}
"""

RETURN = r"""
name:
  description: >-
    The name of the variable.
  returned: success
  type: str

value:
  description: >-
    The value of the variable.
  returned: success
  type: str

created_at:
  description: >-
    The date and time at which the variable was created, in ISO 8601 format':' YYYY-MM-DDTHH:MM:SSZ.
  returned: success
  type: str

updated_at:
  description: >-
    The date and time at which the variable was last updated, in ISO 8601 format':' YYYY-MM-DDTHH:MM:SSZ.
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
    """Retrieve the current state of the action_variable via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    name = module.params.get("name")
    search_key = "name"
    search_value = name if identifier is None else identifier

    if search_value is None:
        return None
    try:
        items = client.get("/repos/{owner}/{repo}/actions/variables")
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

    if module.params.get("name") is not None:
        payload["name"] = module.params["name"]

    if module.params.get("selected_repository_ids") is not None:
        payload["selected_repository_ids"] = module.params["selected_repository_ids"]

    if module.params.get("value") is not None:
        payload["value"] = module.params["value"]

    if module.params.get("visibility") is not None:
        payload["visibility"] = module.params["visibility"]

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),

            name=dict(
                type="str",





            ),

            selected_repository_ids=dict(
                type="list",





            ),

            value=dict(
                type="str",





            ),

            visibility=dict(
                type="str",


                choices=['all', 'private', 'selected'],




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
                        "/repos/{owner}/{repo}/actions/variables",
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

                result["name"] = current.get("name")

                result["value"] = current.get("value")

                result["created_at"] = current.get("created_at")

                result["updated_at"] = current.get("updated_at")


        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/repos/{owner}/{repo}/actions/variables/{name}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)


    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
