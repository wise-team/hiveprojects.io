{% for item in items %}

## {{ item.project.name }}
**Team:** {{ item.hive_team_members }}

![]({{ item.project_image_url }})

**Category:** [{{item.category_name}}]({{item.category_url}})

**Description:** *{{ item.project.description }}*

[{{item.project.name}} on HiveProjects.io]({{item.project_url}})

{% endfor %}
