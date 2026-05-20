#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: autolink
short_description: Manage repos
version_added: "1.0.0"
description:
  - Create, update, and delete autolink resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the autolink resource.
    type: str
    choices: ['present', 'absent']
    default: present

  key_prefix:
    description:
      - >-
        This prefix appended by certain characters will generate a link any time it is found in an...
    type: str

    required: true





  url_template:
    description:
      - >-
        The URL must contain <num> for the reference number. <num> matches different characters...
    type: str

    required: true





  is_alphanumeric:
    description:
      - >-
        Whether this autolink reference matches alphanumeric characters. If true, the <num> parameter of...
    type: bool



    default: true



extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""

- name: Create a autolink
  stevefulme1.github.autolink:


    key_prefix: "example_key_prefix"



    url_template: "example_url_template"




    state: present
  # API: POST /repos/{owner}/{repo}/autolinks



- name: Update a autolink
  stevefulme1.github.autolink:
    id: "existing_id"






    is_alphanumeric: "updated_is_alphanumeric"


    state: present
  # API:  



- name: Delete a autolink
  stevefulme1.github.autolink:
    id: "existing_id"
    state: absent
  # API: DELETE /repos/{owner}/{repo}/autolinks/{autolink_id}

"""

RETURN = r"""

id:
  description: >-
    
  returned: success
  type: int


key_prefix:
  description: >-
    The prefix of a key that is linkified.
  returned: success
  type: str


url_template:
  description: >-
    A template for the target URL that is generated if a key was found.
  returned: success
  type: str


is_alphanumeric:
  description: >-
    Whether this autolink reference matches alphanumeric characters. If false, this autolink...
  returned: success
  type: bool


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
    """Retrieve the current state of the autolink via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    search_key = "id"
    search_value = identifier

    if search_value is None:
        return None
    try:
        items = client.get("/repos/{owner}/{repo}/autolinks")
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

    if module.params.get("key_prefix") is not None:
        payload["key_prefix"] = module.params["key_prefix"]

    if module.params.get("url_template") is not None:
        payload["url_template"] = module.params["url_template"]

    if module.params.get("is_alphanumeric") is not None:
        payload["is_alphanumeric"] = module.params["is_alphanumeric"]

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),

            key_prefix=dict(
                type="str",

                required=True,





            ),

            url_template=dict(
                type="str",

                required=True,





            ),

            is_alphanumeric=dict(
                type="bool",



                default=true,



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
                        "/repos/{owner}/{repo}/autolinks",
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

                result["key_prefix"] = current.get("key_prefix")

                result["url_template"] = current.get("url_template")

                result["is_alphanumeric"] = current.get("is_alphanumeric")

                result["updated_at"] = current.get("updated_at")


        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/repos/{owner}/{repo}/autolinks/{autolink_id}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)


    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
