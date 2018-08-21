from sqlalchemy.types import UserDefinedType, BINARY
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Fqdn(UserDefinedType):

    impl = BINARY(16)

    def get_col_spec(self, **kw):
        return "FQDN"

    def bind_processor(self, dialect):

        DBAPIBinary = dialect.dbapi.Binary

        def process(value):
            if isinstance(value, str):
                value = value.encode('utf-8')

            return DBAPIBinary(value)

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return value

        return process

    @property
    def python_type(self):
        return self.impl.type.python_type