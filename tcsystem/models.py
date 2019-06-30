from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey


class Order(models.Model):
    title = models.CharField(max_length=256, blank=True)
    text = models.TextField()
    date = models.DateTimeField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_hash = models.CharField(max_length=64)
    number = models.CharField(max_length=32, blank=True)
    is_closed = models.BooleanField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField()
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return self.text[:min(len(self.text), 20)] + '...'


class Group(MPTTModel):
    title = models.CharField(max_length=256)
    members = models.ManyToManyField(
        User,
        related_name='members',
        null=True,
        blank=True
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title


class PersonalGroup(models.Model):
    title = models.CharField(max_length=256)
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='creators'
    )
    members = models.ManyToManyField(User, related_name='pmembers')

    def __str__(self):
        return self.title


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='to_sender'
    )
    text = models.TextField()
    date = models.DateTimeField()
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Chat(models.Model):
    first_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='to_first'
    )
    second_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='to_second'
    )

    def __str__(self):
        return str(self.number)


class UserOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_accepted = models.BooleanField()
    is_completed = models.BooleanField()

    def __str__(self):
        return str(self.user.userprofile) + ' - ' + str(self.order)


class Signature(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    signer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True)
    signature = models.BinaryField(editable=True, null=True)
    is_correct = models.BooleanField()

    def __str__(self):
        return str(self.id)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=256, null=True, blank=True)
    cert = models.TextField(null=True, blank=True)
    position = models.CharField(max_length=150)
    about = models.TextField(null=True, blank=True)

    def __str__(self):
        name = ''
        if self.user.last_name:
            name = name + self.user.last_name
        else:
            return self.user.username
        if self.user.first_name:
            name = name + ' ' + self.user.first_name[0] + '.'
        if self.middle_name:
            name = name + ' ' + self.middle_name[0] + '.'
        return name


class CA(models.Model):
    title = models.CharField(max_length=256)
    cert = models.TextField()

    def __str__(self):
        return self.title
