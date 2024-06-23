from App import models


class ObjFactory:
    def get_user(self, username):
        return models.User.objects.create_user(
            username=username,
            password=username,
            email=f'{username}@gmail.com',
        )

    def get_post(self, user, title, content, **kwargs):
        return models.Post.objects.create(
            user=user,
            title=title,
            content=content,
            **kwargs
        )

    def get_comment(self, user, post, content, **kwargs):
        return models.Comment.objects.create(
            user=user,
            post=post,
            content=content,
            **kwargs
        )

    def get_reply(self, user, comment, content, **kwargs):
        return self.get_comment(
            user, comment.post, content, comment=comment, **kwargs)

    def get_tag(self, name):
        return models.Tag.objects.create(name=name)

    def get_category(self, name):
        return models.Category.objects.create(name=name)
