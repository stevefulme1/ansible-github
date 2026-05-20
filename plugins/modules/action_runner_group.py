#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: action_runner_group
short_description: Manage actions
version_added: "1.0.0"
description:
  - Create, update, and delete action_runner-group resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the action_runner-group resource.
    type: str
    choices: ['present', 'absent']
    default: present

  name:
    description:
      - >-
        Name of the runner group.
    type: str

    required: true





  allows_public_repositories:
    description:
      - >-
        Whether the runner group can be used by public repositories.
    type: bool



    default: false



  network_configuration_id:
    description:
      - >-
        The identifier of a hosted compute network configuration.
    type: str





  restricted_to_workflows:
    description:
      - >-
        If true, the runner group will be restricted to running only the workflows specified in the...
    type: bool



    default: false



  runners:
    description:
      - >-
        List of runner IDs to add to the runner group.
    type: list





  selected_repository_ids:
    description:
      - >-
        List of repository IDs that can access the runner group.
    type: list





  selected_workflows:
    description:
      - >-
        List of workflows the runner group should be allowed to run. This setting will be ignored unless...
    type: list





  visibility:
    description:
      - >-
        Visibility of a runner group. You can select all repositories, select individual repositories,...
    type: str


    choices: ["selected", "all", "private"]




extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""

- name: Create a action_runner-group
  stevefulme1.github.action_runner_group:


    name: "example_name"
















    state: present
  # API: POST /orgs/{org}/actions/runner-groups



- name: Update a action_runner-group
  stevefulme1.github.action_runner_group:
    id: "existing_id"




    allows_public_repositories: "updated_allows_public_repositories"



    network_configuration_id: "updated_network_configuration_id"



    restricted_to_workflows: "updated_restricted_to_workflows"



    runners: "updated_runners"



    selected_repository_ids: "updated_selected_repository_ids"



    selected_workflows: "updated_selected_workflows"



    visibility: "updated_visibility"


    state: present
  # API:  



- name: Delete a action_runner-group
  stevefulme1.github.action_runner_group:
    id: "existing_id"
    state: absent
  # API: DELETE /orgs/{org}/actions/runner-groups/{runner_group_id}

"""

RETURN = r"""

id:
  description: >-
    
  returned: success
  type: float


name:
  description: >-
    
  returned: success
  type: str


visibility:
  description: >-
    
  returned: success
  type: str


default:
  description: >-
    
  returned: success
  type: bool


selected_repositories_url:
  description: >-
    Link to the selected repositories resource for this runner group. Not present unless visibility...
  returned: success
  type: str


runners_url:
  description: >-
    
  returned: success
  type: str


hosted_runners_url:
  description: >-
    
  returned: success
  type: str


network_configuration_id:
  description: >-
    The identifier of a hosted compute network configuration.
  returned: success
  type: str


inherited:
  description: >-
    
  returned: success
  type: bool


inherited_allows_public_repositories:
  description: >-
    
  returned: success
  type: bool


allows_public_repositories:
  description: >-
    
  returned: success
  type: bool


workflow_restrictions_read_only:
  description: >-
    If true, the restricted_to_workflows and selected_workflows fields cannot be modified.
  returned: success
  type: bool


restricted_to_workflows:
  description: >-
    If true, the runner group will be restricted to running only the workflows specified in the...
  returned: success
  type: bool


selected_workflows:
  description: >-
    List of workflows the runner group should be allowed to run. This setting will be ignored unless...
  returned: success
  type: list


"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.github.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def get_current_state(client, module):
    """Retrieve the current state of the action_runner-group via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    name = module.params.get("name")
    search_key = "name"
    search_value = name if identifier is None else identifier

    if search_value is None:
        return None
    try:
        items = client.get("/orgs/{org}/actions/runner-groups")
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

    if module.params.get("allows_public_repositories") is not None:
        payload["allows_public_repositories"] = module.params["allows_public_repositories"]

    if module.params.get("network_configuration_id") is not None:
        payload["network_configuration_id"] = module.params["network_configuration_id"]

    if module.params.get("restricted_to_workflows") is not None:
        payload["restricted_to_workflows"] = module.params["restricted_to_workflows"]

    if module.params.get("runners") is not None:
        payload["runners"] = module.params["runners"]

    if module.params.get("selected_repository_ids") is not None:
        payload["selected_repository_ids"] = module.params["selected_repository_ids"]

    if module.params.get("selected_workflows") is not None:
        payload["selected_workflows"] = module.params["selected_workflows"]

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

                required=True,





            ),

            allows_public_repositories=dict(
                type="bool",



                default=false,



            ),

            network_configuration_id=dict(
                type="str",





            ),

            restricted_to_workflows=dict(
                type="bool",



                default=false,



            ),

            runners=dict(
                type="list",





            ),

            selected_repository_ids=dict(
                type="list",





            ),

            selected_workflows=dict(
                type="list",





            ),

            visibility=dict(
                type="str",


                choices=['selected', 'all', 'private'],




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
                        "/orgs/{org}/actions/runner-groups",
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

                result["name"] = current.get("name")

                result["visibility"] = current.get("visibility")

                result["default"] = current.get("default")

                result["selected_repositories_url"] = current.get("selected_repositories_url")

                result["runners_url"] = current.get("runners_url")

                result["hosted_runners_url"] = current.get("hosted_runners_url")

                result["network_configuration_id"] = current.get("network_configuration_id")

                result["inherited"] = current.get("inherited")

                result["inherited_allows_public_repositories"] = current.get("inherited_allows_public_repositories")

                result["allows_public_repositories"] = current.get("allows_public_repositories")

                result["workflow_restrictions_read_only"] = current.get("workflow_restrictions_read_only")

                result["restricted_to_workflows"] = current.get("restricted_to_workflows")

                result["selected_workflows"] = current.get("selected_workflows")


        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/orgs/{org}/actions/runner-groups/{runner_group_id}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)


    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
