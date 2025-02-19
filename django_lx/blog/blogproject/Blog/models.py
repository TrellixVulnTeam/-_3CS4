from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import markdown
from django.utils.html import strip_tags
# Create your models here.
class Category(models.Model):
    '''
    分类 Category
     Django 要求模型必须继承 models.Model 类。
    Category 只需要一个简单的分类名 name 就可以了。
    CharField 指定了分类名 name 的数据类型，CharField 是字符型，
    CharField 的 max_length 参数指定其最大长度，超过这个长度的分类名就不能被存入数据库。
    当然 Django 还为我们提供了多种其它的数据类型
    如日期时间类型 DateTimeField、整数类型 IntegerField 等等。
    '''
    name = models.CharField(max_length=100)
    def __str__(self):

        return self.name
class Tag(models.Model):
    """
        标签 Tag 也比较简单，和 Category 一样。
        再次强调一定要继承 models.Model 类！
    """
    name=models.CharField(max_length=100)
    def __str__(self):
        return self.name
class Post(models.Model):
    title=models.CharField(max_length=70)

    # 文章正文，我们使用了 TextField。
    # 存储比较短的字符串可以使用 CharField
    # 但对于文章的正文来说可能会是一大段文本，因此使用 TextField 来存储大段文本.
    body=models.TextField()


    # 这两个列分别表示文章的创建时间和最后一次修改时间
    # 存储时间的字段用 DateTimeField 类型。
    created_time=models.DateTimeField()
    modified_time=models.DateTimeField()

    # 文章摘要，可以没有文章摘要，但默认情况下 CharField 要求我们必须存入数据，否则就会报错。
    # 指定 CharField 的 blank=True 参数值后就可以允许空值了。
    excerpt=models.CharField(max_length=200,blank=True)

    # 这是分类与标签，分类与标签的模型我们已经定义在上面。
    # 我们在这里把文章对应的数据库表和分类、标签对应的数据库表关联了起来，但是关联形式稍微有点不同。
    # 我们规定一篇文章只能对应一个分类，但是一个分类下可以有多篇文章
    # 所以我们使用的是 ForeignKey，即一对多的关联关系。
    # 而对于标签来说，一篇文章可以有多个标签，同一个标签下也可能有多篇文章
    # 所以我们使用 ManyToManyField，表明这是多对多的关联关系。
    # 同时我们规定文章可以没有标签，因此为标签 tags 指定了 blank=True。
    category=models.ForeignKey(Category)
    tags=models.ManyToManyField(Tag,blank=True)

    # 文章作者，这里 User 是从 django.contrib.auth.models 导入的。
    # django.contrib.auth 是 Django 内置的应用
    # 专门用于处理网站用户的注册、登录等流程，User 是 Django 为我们已经写好的用户模型。
    # 这里我们通过 ForeignKey 把文章和 User 关联了起来。
    # 因为我们规定一篇文章只能有一个作者，而一个作者可能会写多篇文章
    # 因此这是一对多的关联关系，和 Category 类似。
    author=models.ForeignKey(User)

    # PositiveIntegerField，该类型的值只允许为正整数或 0，初始化为0
    views=models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('Blog:detail',kwargs={'pk':self.pk})

    class Meta:
        ordering = ['-created_time']

    #increase_views 方法首先将自身对应的 views 字段的值 +1
    # （此时数据库中的值还没变），然后调用 save 方法将更改后的值保存到数据库。
    # 这里使用了 update_fields
    # 参数来告诉 Django 只更新数据库中 views 字段的值，以提高效率。
    def increase_views(self):
        self.views+=1
        self.save(update_fields=['views'])
    def save(self,*args,**kwargs):
        #  *args可以当作可容纳多个变量组成的list
        # **kwargs可以当作容纳多个key和value的dictionary
        if not self.excerpt:
            # 首先实例化一个 Markdown 类，用于渲染 body 的文本
            md=markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # 将 Markdown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 54 个字符赋给 excerpt
            self.excerpt=strip_tags(md.convert(self.body))[:54]
        # 调用父类的 save方法将数据保存到数据库中
        super(Post, self).save(*args,**kwargs)