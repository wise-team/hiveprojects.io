from django.db import models
from django.utils.translation import ugettext_lazy as _

from package.models import BaseModel, Project


class UpdatePost(BaseModel):
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    body_text = models.TextField(_("Post Body Text"), blank=True, null=True)
    projects = models.ManyToManyField(Project)
