#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulmer)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: team
short_description: Manage enterprise-teams
version_added: "1.0.0"
description:
  - Create, update, and delete team resources.
  - Supports check mode and diff mode for safe operations.
author:
  - "Steve Fulmer (@stevefulmer)"
options:
  state:
    description:
      - Desired state of the team resource.
    type: str
    choices: ['present', 'absent']
    default: present

  name:
    description:
      - >-
        The name of the team.
    type: str

    required: true

  description:
    description:
      - >-
        The description of the team.
    type: str

  group_id:
    description:
      - >-
        The ID of the IdP group to assign team membership with. The new IdP group will replace the...
    type: str

  maintainers:
    description:
      - >-
        List GitHub usernames for organization members who will become team maintainers.
    type: list

  notification_setting:
    description:
      - >-
        The notification setting the team has chosen. Editing teams without specifying this parameter...
    type: str

    choices: ["notifications_enabled", "notifications_disabled"]

  organization_selection_type:
    description:
      - >-
        Specifies which organizations in the enterprise should have access to this team. Can be one of...
    type: str

    choices: ["disabled", "selected", "all"]

    default: "disabled"

  parent_team_id:
    description:
      - >-
        The ID of a team to set as the parent team.
    type: int

  permission:
    description:
      - >-
        Closing down notice. The permission that new repositories will be added to the team with when...
    type: str

    choices: ["pull", "push", "admin"]

    default: "pull"

  privacy:
    description:
      - >-
        The level of privacy this team should have. Editing teams without specifying this parameter...
    type: str

    choices: ["secret", "closed"]

  repo_names:
    description:
      - >-
        The full name (e.g., "organization-name/repository-name") of repositories to add the team to.
    type: list

  sync_to_organizations:
    description:
      - >-
        Retired: this field is no longer supported. Whether the enterprise team should be reflected in...
    type: str

    choices: ["all", "disabled"]

    default: "disabled"

extends_documentation_fragment:
  - stevefulme1.github.auth
"""

EXAMPLES = r"""
- name: Create a team
  stevefulme1.github.team:

    name: "example_name"

    state: present
  # API: POST /orgs/{org}/teams

- name: Update a team
  stevefulme1.github.team:
    id: "existing_id"

    description: "updated_description"

    group_id: "updated_group_id"

    maintainers: "updated_maintainers"

    notification_setting: "updated_notification_setting"

    organization_selection_type: "updated_organization_selection_type"

    parent_team_id: "updated_parent_team_id"

    permission: "updated_permission"

    privacy: "updated_privacy"

    repo_names: "updated_repo_names"

    sync_to_organizations: "updated_sync_to_organizations"

    state: present
  # API:

- name: Delete a team
  stevefulme1.github.team:
    id: "existing_id"
    state: absent
  # API: DELETE /teams/{team_id}
"""

RETURN = r"""
id:
  description: >-
    Unique identifier of the team
  returned: success
  type: int

node_id:
  description: >-

  returned: success
  type: str

url:
  description: >-
    URL for the team
  returned: success
  type: str

html_url:
  description: >-

  returned: success
  type: str

name:
  description: >-
    Name of the team
  returned: success
  type: str

slug:
  description: >-

  returned: success
  type: str

description:
  description: >-

  returned: success
  type: str

privacy:
  description: >-
    The level of privacy this team should have
  returned: success
  type: str

notification_setting:
  description: >-
    The notification setting the team has set
  returned: success
  type: str

permission:
  description: >-
    Permission that the team will have for its repositories
  returned: success
  type: str

members_url:
  description: >-

  returned: success
  type: str

repositories_url:
  description: >-

  returned: success
  type: str

parent:
  description: >-
    Groups of organization members that gives permissions on specified repositories.
  returned: success
  type: dict

members_count:
  description: >-

  returned: success
  type: int

repos_count:
  description: >-

  returned: success
  type: int

created_at:
  description: >-

  returned: success
  type: str

updated_at:
  description: >-

  returned: success
  type: str

organization:
  description: >-
    Team Organization
  returned: success
  type: dict

ldap_dn:
  description: >-
    The distinguished name (DN) of the LDAP entry to map to a team.
  returned: success
  type: str

type:
  description: >-
    The ownership type of the team
  returned: success
  type: str

organization_id:
  description: >-
    Unique identifier of the organization to which this team belongs
  returned: success
  type: int

enterprise_id:
  description: >-
    Unique identifier of the enterprise to which this team belongs
  returned: success
  type: int
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.github.plugins.module_utils.api_client import (
    Client,
    ClientError,
    argument_spec as auth_argument_spec,
)


def get_current_state(client, module):
    """Retrieve the current state of the team via GET."""

    # No single-resource GET endpoint; fall back to list + filter
    identifier = module.params.get("id")

    name = module.params.get("name")
    search_key = "name"
    search_value = name if identifier is None else identifier

    if search_value is None:
        return None
    try:
        items = client.get("/user/teams")
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

    if module.params.get("description") is not None:
        payload["description"] = module.params["description"]

    if module.params.get("group_id") is not None:
        payload["group_id"] = module.params["group_id"]

    if module.params.get("maintainers") is not None:
        payload["maintainers"] = module.params["maintainers"]

    if module.params.get("notification_setting") is not None:
        payload["notification_setting"] = module.params["notification_setting"]

    if module.params.get("organization_selection_type") is not None:
        payload["organization_selection_type"] = module.params["organization_selection_type"]

    if module.params.get("parent_team_id") is not None:
        payload["parent_team_id"] = module.params["parent_team_id"]

    if module.params.get("permission") is not None:
        payload["permission"] = module.params["permission"]

    if module.params.get("privacy") is not None:
        payload["privacy"] = module.params["privacy"]

    if module.params.get("repo_names") is not None:
        payload["repo_names"] = module.params["repo_names"]

    if module.params.get("sync_to_organizations") is not None:
        payload["sync_to_organizations"] = module.params["sync_to_organizations"]

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

            description=dict(
                type="str",

            ),

            group_id=dict(
                type="str",

            ),

            maintainers=dict(
                type="list",

            ),

            notification_setting=dict(
                type="str",

                choices=['notifications_enabled', 'notifications_disabled'],

            ),

            organization_selection_type=dict(
                type="str",

                choices=['disabled', 'selected', 'all'],

                default="disabled",

            ),

            parent_team_id=dict(
                type="int",

            ),

            permission=dict(
                type="str",

                choices=['pull', 'push', 'admin'],

                default="pull",

            ),

            privacy=dict(
                type="str",

                choices=['secret', 'closed'],

            ),

            repo_names=dict(
                type="list",

            ),

            sync_to_organizations=dict(
                type="str",

                choices=['all', 'disabled'],

                default="disabled",

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
                        "/orgs/{org}/teams",
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

                result["html_url"] = current.get("html_url")

                result["name"] = current.get("name")

                result["slug"] = current.get("slug")

                result["description"] = current.get("description")

                result["privacy"] = current.get("privacy")

                result["notification_setting"] = current.get("notification_setting")

                result["permission"] = current.get("permission")

                result["members_url"] = current.get("members_url")

                result["repositories_url"] = current.get("repositories_url")

                result["parent"] = current.get("parent")

                result["members_count"] = current.get("members_count")

                result["repos_count"] = current.get("repos_count")

                result["created_at"] = current.get("created_at")

                result["updated_at"] = current.get("updated_at")

                result["organization"] = current.get("organization")

                result["ldap_dn"] = current.get("ldap_dn")

                result["type"] = current.get("type")

                result["organization_id"] = current.get("organization_id")

                result["enterprise_id"] = current.get("enterprise_id")

        elif state == "absent":
            if current is not None:
                result["changed"] = True
                result["diff"]["before"] = current
                result["diff"]["after"] = {}

                if not module.check_mode:

                    identifier = current.get("id")
                    path = "/teams/{team_id}".replace(
                        "{id}", str(identifier)
                    )
                    client.delete(path)

    except ClientError as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
