# -*- coding: utf-8 -*-
#!/usr/bin/env python

import json
import os
import pyhs2
import requests
import subprocess
import sys
import tempfile

from datetime import datetime, timedelta

class HiveClient(object):
    def __init__(self, db_host, user, password, database, port=10000, authMechanism="PLAIN"):
        """
        create connection to hive server2
        """
        self.conn = pyhs2.connect(host=db_host,
                                  port=port,
                                  authMechanism=authMechanism,
                                  user=user,
                                  password=password,
                                  database=database,
                                  )

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        if self.conn:
            self.conn.close()
    
    def format_sql(self, sql):
        params = {
            'TODAY': datetime.now().strftime('%Y-%m-%d'),
            'today': datetime.now().strftime('%Y%m%d'),
            'YESTERDAY': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'yesterday': (datetime.now() - timedelta(days=1)).strftime('%Y%m%d'),
            'TOMORROW': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'tomorrow': (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
        }

        if sql:
            for argkey, argvalue in params.items():
                sql = sql.replace('${' + argkey + '}', str(argvalue))

        return sql
    
    def query(self, sql):
        """
        query
        """
        with self.conn.cursor() as cursor:
            cursor.execute(self.format_sql(sql))
            return cursor.fetch()

    def execute(self, sql):
        """
        execute
        """
        with self.conn.cursor() as cursor:
            cursor.execute(self.format_sql(sql))
        

    def close(self):
        """
        close connection
        """
        self.conn.close()
        self.conn = None

def get_popwnd_info(pop_id):
    request_url = "http://pc.ts.2345.com/newTs/web/index.php/api/popupInfo/index/{}".format(pop_id)
    ret = requests.get(request_url)
    if ret.status_code == 200:
        json_ret = ret.json()
        if json_ret['status'] == 'success':
            return json_ret['data']
        else:
            return None

def main():
    """
    main process
    """
    query_new_ids_sql = """
        select
          a.pop_id
        from (
          select
           pop_id 
          from dw_db.dw_pinyin_promotion_popwnd 
          where p_dt='${YESTERDAY}' 
          and pop_id is not null 
          group by
           pop_id
        ) a
        left join dim_db.dim_pinyin_popwnd b 
        on a.pop_id = b.pop_id
        where b.pop_id is null
    """
    popids_name = os.path.join(tempfile.mkdtemp(), 'popids.txt')
    new_pop_cn = 0
    with HiveClient(db_host='master2', port=10000, user='hadoop', password='hadoop', database='default', authMechanism='PLAIN') as hive_client, open(popids_name, 'wb') as jsonfp:
        result = hive_client.query(query_new_ids_sql)
        for res in result:
            pop_prop = get_popwnd_info(res[0])
            if pop_prop:
                jsonfp.write(json.dumps(pop_prop) + '\n')
                new_pop_cn += 1
            else:
                print('get pop info fail')

    print('fetch %d new pop info, load into table.' % new_pop_cn)
    # load into temp_table
    load_sql = "load data local inpath '%s' overwrite into table temp_db.dim_pinyin_popwnd" % popids_name
    p = subprocess.Popen('hive -e "%s" ' % load_sql, shell=True)
    p.wait()
    if p.returncode != 0:
        print('load data into temp table fail.')
        os.unlink(popids_name)
        sys.exit(1)

    os.unlink(popids_name)

if __name__ == '__main__':
    main()

