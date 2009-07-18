# imports # {{{ 
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from datetime import datetime
import string, os, random, time
# }}} 

def get_random_id(*args):
    digits = string.digits + string.letters
    args = list(args)
    args.append(os.urandom(20))
    args.append(time.time())
    random.seed(str(args))
    return "".join(random.choice(digits) for i in range(4))


ACTION_CHOICES = (
    ('r', 'Redirect To'),
    ('f', '"Forward" to View'),
    ('i', 'Inline the URL'),
    ('m', 'Call Model.render()'),
)

# TinyURL # {{{ 
class TinyURL(models.Model):
    tiny_id = models.CharField(max_length=10, primary_key=True)

    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)

    content_object = generic.GenericForeignKey('content_type', 'object_id')

    action = models.CharField(max_length=2, choices=ACTION_CHOICES)
    # action can be like:
    # 1. r:/help/ => redirect to /help/ 
    # 2. v:myapp.myview.myfun => "forward" request to myfun, retaining url
    # 3. i:http://google.com => frame google with our bar
    data = models.CharField(max_length=200)

    created_on = models.DateTimeField(default=datetime.now) 
    
    def __unicode__(self): return "%s: %s" % (
        self.tiny_id, self.content_object
    )

    def save(self, *args, **kw):
        if not self.tiny_id:
            while True:
                self.tiny_id = get_random_id(self.__dict__)
                try:
                    TinyURL.objects.get(tiny_id=self.tiny_id)
                except TinyURL.DoesNotExist:
                    break
                else:
                    print "ID_CLASH", self.tiny_id
        super(TinyURL, self).save(*args, **kw)
# }}} 

# TinyURLBase # {{{ 
class TinyURLBase(models.Model):
    tiny_url = generic.GenericRelation(TinyURL)

    class Meta: 
        abstract = True

    def get_tiny_url(self): return "/" + self.tiny_url.get().tiny_id
# }}}  

# TinyURLForwarder # {{{ 
class TinyURLForwarder(TinyURLBase):
    class Meta:
        abstract = True

    def save(self, *args, **kw):
        super(TinyURLForwarder, self).save(*args, **kw)
        if not self.tiny_url.count():
            self.tiny_url.create(action="v", data=self.__class__.view)
# }}} 

# TinyURLRedirector # {{{ 
class TinyURLRedirector(TinyURLBase):
    class Meta:
        abstract = True

    def save(self, *args, **kw):
        super(TinyURLRedirector, self).save(*args, **kw)
        if not self.tiny_url.count():
            self.tiny_url.create(action="r", data=self.get_absolute_url())
# }}}  
