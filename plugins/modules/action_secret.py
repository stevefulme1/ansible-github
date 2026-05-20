#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: action_secret
short_description: Manage actions
version_added: "1.0.0"
description:
  - Create, update, and delete action_secret resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the action_secret resource.
    type: str
    choices: ['present', 'absent']
    default: present

  encrypted_value:
    description:
      - >-
        Value for your secret, encrypted with LibSodium using the public key retrieved from the Get a...
    type: str

    required: true

  key_id:
    description:
      - >-
        ID of the key you used to encrypt the secret.
    type: str

    required: true

  visibility:
    description:
      - >-
        Which type of organization repositories have access to the organization secret. selected means...
    type: str

    required: true

    choices: ["all", "private", "selected"]

  selected_repository_ids:
    description:
      - >-
        An array of repository ids that can access the organization secret. You can only provide a list...
    type: list
    elements: str

extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""
- name: Update a action_secret
  stevefulme1.github.action_secret:
    id: "existing_id"

    selected_repository_ids: "updated_selected_repository_ids"

    state: present
  # API:

- name: Delete a action_secret
  stevefulme1.github.action_secret:
    id: "existing_id"
    state: absent
  # API: DELETE /repos/{owner}/{repo}/actions/secrets/{secret_name}
"""

RETURN = r"""
name:
  description: >-
    The name of the secret.
  returned: success
  type: str

created_at:
  description: >-

  returned: success
  type: str

updated_at:
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
    """Retrieve the current state of the action_secret via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    name = module.params.get("name")
    search_key = "name"
    search_value = name if identifier is None else identifier

    if search_value is None:
        return None
    try:
        items = client.get("/repos/{owner}/{repo}/actions/secrets")
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

    if module.params.get("encrypted_value") is not None:
        payload["encrypted_value"] = module.params["encrypted_value"]

    if module.params.get("key_id") is not None:
        payload["key_id"] = module.params["key_id"]

    if module.params.get("visibility") is not None:
        payload["visibility"] = module.params["visibility"]

    if module.params.get("selected_repository_ids") is not None:
        payload["selected_repository_ids"] = module.params["selected_repository_ids"]

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),

            encrypted_value=dict(
                type="str",

                required=True,

            ),

            key_id=dict(
                type="str",

                required=True,

            ),

            visibility=dict(
                type="str",

                required=True,

                choices=['all', 'private', 'selected'],

            ),

            selected_repository_ids=dict(
                type="list",
                elements="str",

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

                result["name"] = current.get("name")

                result["created_at"] = current.get("created_at")

                result["updated_at"] = current.get("updated_at")

        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/repos/{owner}/{repo}/actions/secrets/{secret_name}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
