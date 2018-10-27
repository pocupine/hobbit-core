# -*- encoding: utf-8 -*-
import enum
import six

from sqlalchemy import Integer, Column, ForeignKey, func, DateTime


class SurrogatePK(object):
    """A mixin that add ``id``、``created_at`` and ``updated_at`` columns
    to any declarative-mapped class.

    **id**: A surrogate integer 'primary key' column.

    **created_at**: Auto save ``datetime.now()`` when row created.

    **updated_at**: Auto save ``datetime.now()`` when row updated.
    """

    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(),
        onupdate=func.now())

    def __repr__(self):
        """You can set label property.

        Returns:
            str: ``<{classname}({pk}:{label!r})>``
        """
        return '<{classname}({pk}:{label!r})>'.format(
            classname=type(self).__name__, pk=self.id,
            label=getattr(self, 'label', ''))


def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Args:
        tablename (str): Model.__table_name__.
        nullable (bool): Default is False.
        pk_name (str): Primary column's name.

    Others:

    See ``sqlalchemy.Column``

    Examples::

        from sqlalchemy.orm import relationship

        role_id = reference_col('role')
        role = relationship('Role', backref='users', cascade='all, delete')
    """

    return Column(
        ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)


class EnumExt(enum.Enum):
    """ Extension for serialize/deserialize sqlalchemy enum field.

    Be sure ``type(key)`` is ``int`` and ``type(value)`` is ``str``
    (``label = (key, value)``).

    Examples::

        class TaskState(EnumExt):
            # label = (key, value)
            CREATED = (0, '新建')
            PENDING = (1, '等待')
            STARTING = (2, '开始')
            RUNNING = (3, '运行中')
            FINISHED = (4, '已完成')
            FAILED = (5, '失败')
    """

    @classmethod
    def strict_dump(cls, key, verbose=False):
        pos = 1 if verbose else 0
        return cls[key].value[pos]

    @classmethod
    def dump(cls, label, verbose=False):
        """Dump one label to option.

        Examples::

            TaskState.dump('CREATED')  # {'key': 0, 'value': '新建'}

        Returns:

            dict: Dict of label's key and value. If label not exist,
            raise ``KeyError``.
        """

        ret = {'key': cls[label].value[0], 'value': cls[label].value[1]}
        if verbose:
            ret.update({'label': label})
        return ret

    @classmethod
    def load(cls, val):
        """Get label by key or value.

        Examples::

            TaskState.load(4)  # 'FINISHED'
            TaskState.load('新建')  # 'CREATED'

        Returns:
            str|None: Label.
        """

        pos = 1 if isinstance(val, six.string_types) else 0
        for elem in cls:
            if elem.value[pos] == val:
                return elem.name

    @classmethod
    def to_opts(cls, verbose=False):
        """Enum to options.

        Examples::

            opts = TaskState.to_opts(verbose=True)
            print(opts)

            [{'key': 0, 'label': 'CREATED', 'value': u'新建'}, ...]

        Returns:
            list: List of dict which key is `key`, `value`, label.
        """

        opts = []
        for elem in cls:
            opt = {'key': elem.value[0], 'value': elem.value[1]}
            if verbose:
                opt.update({'label': elem.name})
            opts.append(opt)
        return opts
