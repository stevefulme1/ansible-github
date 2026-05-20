#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: repository_collaborator
short_description: Manage repos
version_added: "1.0.0"
description:
  - Create, update, and delete repository_collaborator resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the repository_collaborator resource.
    type: str
    choices: ['present', 'absent']
    default: present

  permission:
    description:
      - >-
        The permission to grant the collaborator. Only valid on organization-owned repositories. We...
    type: str



    default: "push"



extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""


- name: Update a repository_collaborator
  stevefulme1.github.repository_collaborator:
    id: "existing_id"


    permission: "updated_permission"


    state: present
  # API:  



- name: Delete a repository_collaborator
  stevefulme1.github.repository_collaborator:
    id: "existing_id"
    state: absent
  # API: DELETE /repos/{owner}/{repo}/collaborators/{username}

"""

RETURN = r"""

login:
  description: >-
    
  returned: success
  type: str


id:
  description: >-
    
  returned: success
  type: int


email:
  description: >-
    
  returned: success
  type: str


name:
  description: >-
    
  returned: success
  type: str


node_id:
  description: >-
    
  returned: success
  type: str


avatar_url:
  description: >-
    
  returned: success
  type: str


gravatar_id:
  description: >-
    
  returned: success
  type: str


url:
  description: >-
    
  returned: success
  type: str


html_url:
  description: >-
    
  returned: success
  type: str


followers_url:
  description: >-
    
  returned: success
  type: str


following_url:
  description: >-
    
  returned: success
  type: str


gists_url:
  description: >-
    
  returned: success
  type: str


starred_url:
  description: >-
    
  returned: success
  type: str


subscriptions_url:
  description: >-
    
  returned: success
  type: str


organizations_url:
  description: >-
    
  returned: success
  type: str


repos_url:
  description: >-
    
  returned: success
  type: str


events_url:
  description: >-
    
  returned: success
  type: str


received_events_url:
  description: >-
    
  returned: success
  type: str


type:
  description: >-
    
  returned: success
  type: str


site_admin:
  description: >-
    
  returned: success
  type: bool


permissions:
  description: >-
    
  returned: success
  type: dict


role_name:
  description: >-
    
  returned: success
  type: str


user_view_type:
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
    """Retrieve the current state of the repository_collaborator via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    name = module.params.get("name")
    search_key = "name"
    search_value = name if identifier is None else identifier

    if search_value is None:
        return None
    try:
        items = client.get("/repos/{owner}/{repo}/collaborators")
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

    if module.params.get("permission") is not None:
        payload["permission"] = module.params["permission"]

    return payload


def main():
    spec = auth_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", choices=["present", "absent"], default="present"),

            permission=dict(
                type="str",



                default="push",



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

                result["login"] = current.get("login")

                result["id"] = current.get("id")

                result["email"] = current.get("email")

                result["name"] = current.get("name")

                result["node_id"] = current.get("node_id")

                result["avatar_url"] = current.get("avatar_url")

                result["gravatar_id"] = current.get("gravatar_id")

                result["url"] = current.get("url")

                result["html_url"] = current.get("html_url")

                result["followers_url"] = current.get("followers_url")

                result["following_url"] = current.get("following_url")

                result["gists_url"] = current.get("gists_url")

                result["starred_url"] = current.get("starred_url")

                result["subscriptions_url"] = current.get("subscriptions_url")

                result["organizations_url"] = current.get("organizations_url")

                result["repos_url"] = current.get("repos_url")

                result["events_url"] = current.get("events_url")

                result["received_events_url"] = current.get("received_events_url")

                result["type"] = current.get("type")

                result["site_admin"] = current.get("site_admin")

                result["permissions"] = current.get("permissions")

                result["role_name"] = current.get("role_name")

                result["user_view_type"] = current.get("user_view_type")


        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/repos/{owner}/{repo}/collaborators/{username}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)


    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
