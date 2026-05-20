#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: issue_label
short_description: Manage issues
version_added: "1.0.0"
description:
  - Create, update, and delete issue_label resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the issue_label resource.
    type: str
    choices: ['present', 'absent']
    default: present

  labels:
    description:
      - >-
        The names of the labels to set for the issue. The labels you set replace any existing labels....
    type: list





extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""

- name: Create a issue_label
  stevefulme1.github.issue_label:



    state: present
  # API: POST /repos/{owner}/{repo}/issues/{issue_number}/labels



- name: Update a issue_label
  stevefulme1.github.issue_label:
    id: "existing_id"


    labels: "updated_labels"


    state: present
  # API:  



- name: Delete a issue_label
  stevefulme1.github.issue_label:
    id: "existing_id"
    state: absent
  # API: DELETE /repos/{owner}/{repo}/issues/{issue_number}/labels/{name}

"""

RETURN = r"""

id:
  description: >-
    Unique identifier for the label.
  returned: success
  type: int


node_id:
  description: >-
    
  returned: success
  type: str


url:
  description: >-
    URL for the label
  returned: success
  type: str


name:
  description: >-
    The name of the label.
  returned: success
  type: str


description:
  description: >-
    Optional description of the label, such as its purpose.
  returned: success
  type: str


color:
  description: >-
    6-character hex code, without the leading , identifying the color
  returned: success
  type: str


default:
  description: >-
    Whether this label comes by default in a new repository.
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
    """Retrieve the current state of the issue_label via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    name = module.params.get("name")
    search_key = "name"
    search_value = name if identifier is None else identifier

    if search_value is None:
        return None
    try:
        items = client.get("/repos/{owner}/{repo}/issues/{issue_number}/labels")
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

    if module.params.get("labels") is not None:
        payload["labels"] = module.params["labels"]

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),

            labels=dict(
                type="list",





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
                        "/repos/{owner}/{repo}/issues/{issue_number}/labels",
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

                result["node_id"] = current.get("node_id")

                result["url"] = current.get("url")

                result["name"] = current.get("name")

                result["description"] = current.get("description")

                result["color"] = current.get("color")

                result["default"] = current.get("default")


        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/repos/{owner}/{repo}/issues/{issue_number}/labels/{name}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)


    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
