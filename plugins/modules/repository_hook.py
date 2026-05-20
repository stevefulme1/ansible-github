#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: repository_hook
short_description: Manage repos
version_added: "1.0.0"
description:
  - Create, update, and delete repository_hook resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the repository_hook resource.
    type: str
    choices: ['present', 'absent']
    default: present

  active:
    description:
      - >-
        Determines if notifications are sent when the webhook is triggered. Set to true to send notifications.
    type: bool



    default: true



  add_events:
    description:
      - >-
        Determines a list of events to be added to the list of events that the Hook triggers for.
    type: list





  config:
    description:
      - >-
        Configuration object of the webhook
    type: dict





  events:
    description:
      - >-
        Determines what events the hook is triggered for. This replaces the entire array of events.
    type: list



    default: ["push"]



  name:
    description:
      - >-
        Use web to create a webhook. Default: web. This parameter only accepts the value web.
    type: str





  remove_events:
    description:
      - >-
        Determines a list of events to be removed from the list of events that the Hook triggers for.
    type: list





extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""

- name: Create a repository_hook
  stevefulme1.github.repository_hook:













    state: present
  # API: POST /repos/{owner}/{repo}/hooks



- name: Update a repository_hook
  stevefulme1.github.repository_hook:
    id: "existing_id"


    active: "updated_active"



    add_events: "updated_add_events"



    config: "updated_config"



    events: "updated_events"



    name: "updated_name"



    remove_events: "updated_remove_events"


    state: present
  # API:  



- name: Delete a repository_hook
  stevefulme1.github.repository_hook:
    id: "existing_id"
    state: absent
  # API: DELETE /repos/{owner}/{repo}/hooks/{hook_id}

"""

RETURN = r"""

type:
  description: >-
    
  returned: success
  type: str


id:
  description: >-
    Unique identifier of the webhook.
  returned: success
  type: int


name:
  description: >-
    The name of a valid service, use 'web' for a webhook.
  returned: success
  type: str


active:
  description: >-
    Determines whether the hook is actually triggered on pushes.
  returned: success
  type: bool


events:
  description: >-
    Determines what events the hook is triggered for. Default: 'push'.
  returned: success
  type: list


config:
  description: >-
    Configuration object of the webhook
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


url:
  description: >-
    
  returned: success
  type: str


test_url:
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


last_response:
  description: >-
    
  returned: success
  type: dict


"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.github.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def get_current_state(client, module):
    """Retrieve the current state of the repository_hook via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    name = module.params.get("name")
    search_key = "name"
    search_value = name if identifier is None else identifier

    if search_value is None:
        return None
    try:
        items = client.get("/repos/{owner}/{repo}/hooks")
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

    if module.params.get("add_events") is not None:
        payload["add_events"] = module.params["add_events"]

    if module.params.get("config") is not None:
        payload["config"] = module.params["config"]

    if module.params.get("events") is not None:
        payload["events"] = module.params["events"]

    if module.params.get("name") is not None:
        payload["name"] = module.params["name"]

    if module.params.get("remove_events") is not None:
        payload["remove_events"] = module.params["remove_events"]

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

            add_events=dict(
                type="list",





            ),

            config=dict(
                type="dict",





            ),

            events=dict(
                type="list",




                default=["push"],




            ),

            name=dict(
                type="str",





            ),

            remove_events=dict(
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
                        "/repos/{owner}/{repo}/hooks",
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

                result["type"] = current.get("type")

                result["id"] = current.get("id")

                result["name"] = current.get("name")

                result["active"] = current.get("active")

                result["events"] = current.get("events")

                result["config"] = current.get("config")

                result["updated_at"] = current.get("updated_at")

                result["created_at"] = current.get("created_at")

                result["url"] = current.get("url")

                result["test_url"] = current.get("test_url")

                result["ping_url"] = current.get("ping_url")

                result["deliveries_url"] = current.get("deliveries_url")

                result["last_response"] = current.get("last_response")


        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/repos/{owner}/{repo}/hooks/{hook_id}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)


    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
