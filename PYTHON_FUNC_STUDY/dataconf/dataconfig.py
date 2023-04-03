"""
https://towardsdatascience.com/configuration-files-in-python-using-dataclasses-ec8528e72e01
"""

from abc import ABCMeta
from dataclasses import dataclass
from dataconf import loads
import pandas as pd
# import pyspark
# from pyspark.sql import SparkSession
from typing import Any, List, Optional, Text, Union


############################
########## Python ##########
############################
class InputData(metaclass=ABCMeta):
    # Replicating Scala sealed trait behavior
    pass


@dataclass
class CSV(InputData):
    # define whatever you need here
    location: Text
    header: Union[Text, int, List[int]] = "infer"
    sep: Optional[Text] = None
    delim: Optional[Text] = None

    def load_df(self) -> pd.DataFrame:
        return pd.read_csv(self.location, header=self.header, sep=self.sep, delimiter=self.delim)


@dataclass
class SQL(InputData):
    # define whatever you need here
    sql: Text
    con: Any  # SQLAlchemy, string, sqllite

    def load_df(self) -> pd.DataFrame:
        return pd.read_sql(self.sql, con=self.conn)


class PipeParams:
    write_path: Text
    input_source: InputData


# by changing the config input_source values, we can access the
# the other dataclasses without the need for branching.
str_conf = """
{
 write_path: "/path/to/save/data"
 input_source {
  sql: "select * from db.table where something"
  con: "connection string"
 }
 # other parameters needed
}
"""

conf = dataconf.loads(str_conf, PipeParams)
df = conf.load_df()

#############################
########## PySpark ##########
#############################
spark = SparkSession.builder.getOrCreate()


class InputType(metaclass=ABCMeta):
    # Replicating Scala sealed trait behavior
    pass


@dataclass
class TableSource(InputType):
    table_name: Text
    filter: Text

    def load_df(self, spark: SparkSession) -> pyspark.sql.dataframe:
        return spark.table(self.table_name).filter(self.filter)


@dataclass
class FileSource(InputType):
    file_path: Text
    format: Text
    filter: Text

    def load_df(self, spark: SparkSession) -> pyspark.sql.dataframe:
        return spark.read.format(self.format).load(self.file_path).filter(self.filter)


@dataclass
class SQLSource(InputType):
    query: Text

    def load_df(self, spark: SparkSession) -> pyspark.sql.dataframe:
        return spark.sql(self.query)


@dataclass
class Params:
    input_source: InputType
    write_path: Text


# by changing the config input_source values, we can access the
# the other dataclasses without they need for branching.
str_conf = """
{
 write_path: "/path/to/save/data"
 input_source {
  table_name: schema.table_name
  filter: "par_day < 20210501 and par_hour = 0"
 }
 # other parameters needed
}
"""

conf = loads(str_conf, Params)
df = conf.load_df()
