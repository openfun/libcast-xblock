"""XBlock for videos stored by Youtube."""

import logging
import pkg_resources
import random
import string
import webob

from django.template import Context, Template
# TODO actually translate the app
from django.utils.translation import ugettext_lazy
# from django.utils.translation import ugettext as _

from xblock.core import XBlock
from xblock.fields import Boolean, Scope, String
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin


logger = logging.getLogger(__name__)


@XBlock.needs('settings')
class LibcastXBlock(StudioEditableXBlockMixin, XBlock):
    """
    Play videos based on a modified videojs player. This XBlock supports
    subtitles and multiple resolutions.
    """
    display_name = String(
        help=ugettext_lazy("The name students see. This name appears in "
                           "the course ribbon and as a header for the video."),
        display_name=ugettext_lazy("Component Display Name"),
        default=ugettext_lazy("New video"),
        scope=Scope.settings
    )

    # Youtube ID
    video_id = String(
        scope=Scope.settings,
        help=ugettext_lazy('Fill this with the ID of the video found in the video uploads dashboard'),
        default="",
        display_name=ugettext_lazy('Video ID')
    )

    is_youtube_video = Boolean(
        help=ugettext_lazy("Is this video stored on youtube?"),
        display_name=ugettext_lazy("Youtube video"),
        scope=Scope.settings,
        default=True
    )

    allow_download = Boolean(
        help=ugettext_lazy("Allow students to download this video."),
        display_name=ugettext_lazy("Video download allowed"),
        scope=Scope.settings,
        default=True
    )

    editable_fields = ('display_name', 'video_id', 'allow_download', )

    def __init__(self, *args, **kwargs):
        super(LibcastXBlock, self).__init__(*args, **kwargs)

    @property
    def course_key_string(self):
        return unicode(self.location.course_key)

    @property
    def resource_slug(self):
        return None if self.video_id is None else self.video_id.strip()

    def get_icon_class(self):
        """CSS class to be used in courseware sequence list."""
        return 'video'

    def is_studio(self):
        studio = False
        try:
            studio = self.runtime.is_author_mode
        except AttributeError:
            pass
        return studio

    def student_view(self, context=None):
        fragment = Fragment()
        if self.is_youtube_video and self.video_id:
            self.get_youtube_content(fragment)
        else:
            self.unavailable_content(fragment)
        return fragment

    def unavailable_content(self, fragment):
        from django.conf import settings  # Bad. We are not supposed to import settings from here.

        template_content = self.resource_string("public/html/unavailable.html")
        template = Template(template_content)
        content = template.render(Context({
            'lms_base': settings.LMS_BASE,
            'is_studio': self.is_studio,
        }))
        fragment.add_content(content)

    def get_youtube_content(self, fragment):
        # iframe element id
        element_id = ''.join([random.choice(string.ascii_lowercase) for _ in range(0, 20)])

        # Add html code
        template_content = self.resource_string("public/html/youtube.html")
        template = Template(template_content)
        context = {
            'display_name': self.display_name,
            'video_id': self.resource_slug,
            'element_id': element_id
        }
        content = template.render(Context(context))
        fragment.add_content(content)

        # Add youtube event logger
        fragment.add_javascript(self.resource_string("public/js/youtube.js"))
        fragment.initialize_js("YoutubePlayer", json_args={
            'course_id': self.course_key_string,
            'video_id': self.resource_slug,
            'element_id': element_id
        })

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")
