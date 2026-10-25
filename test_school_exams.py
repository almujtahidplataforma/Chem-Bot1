import ast, asyncio, unittest
from pathlib import Path
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
ZONE=ZoneInfo('Asia/Baghdad'); NOW=datetime(2026,10,1,18,tzinfo=ZONE)
class Cursor:
 def __init__(self,responses):self.responses=list(responses);self.calls=[]
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def execute(self,sql,args=None):self.calls.append((sql,args))
 def fetchone(self):return self.responses.pop(0)
class Conn:
 def __init__(self,cur):self.cur=cur
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def cursor(self):return self.cur
 def commit(self):pass
async def run(fn):return fn()
def extract(source,name):
 tree=ast.parse(source);return next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
class Windows(unittest.TestCase):
 def check(self,subject,task,extension,expected):
  source=(Path(__file__).parent/'database.py').read_text();cur=Cursor([extension,None,{'status':'approved'},{}])
  ns={'connect':lambda:Conn(cur),'run':run,'datetime_now':lambda cur:NOW,'_v54_ensure_school_review_task':lambda *args:task}
  exec(compile(ast.Module(body=[extract(source,'v54_prepare_school_review_exam')],type_ignores=[]),'<gate>','exec'),ns)
  result=asyncio.run(ns['v54_prepare_school_review_exam'](7,99));self.assertEqual(result['status'],expected)
 def test_all_bots_windows(self):
  for subject in ('arabic',):
   with self.subTest(subject=subject):
    base={'id':42,'deadline':NOW+timedelta(hours=1),'exam_available_at':NOW-timedelta(hours=1),'closed':False,'exam_pending_activation':False}
    self.check(subject,base,{},'open')
    self.check(subject,{**base,'deadline':NOW-timedelta(seconds=1)}, {},'closed')
    self.check(subject,{**base,'deadline':NOW-timedelta(seconds=1)},{'extended_until':NOW+timedelta(hours=2)},'open')
    self.check(subject,{**base,'exam_available_at':NOW+timedelta(hours=1)}, {},'scheduled')
    self.check(subject,{**base,'closed':True},{},'closed')
 def test_parent_cannot_reopen_expired(self):
  for subject in ('arabic',):
   source=(Path(__file__).parent/'database.py').read_text()
   task={'id':42,'school_review_id':7,'exam_duration_hours':24,'deadline':NOW-timedelta(hours=1)}
   review={'exam_deleted':False,'exam_manual_closed':False,'exam_opens_at':NOW-timedelta(days=1),'exam_closes_at':NOW-timedelta(hours=1)}
   cur=Cursor([{'user_id':99},task,review]);ns={'connect':lambda:Conn(cur),'run':run,'datetime_now':lambda cur:NOW,'timedelta':timedelta}
   exec(compile(ast.Module(body=[extract(source,'activate_exam')],type_ignores=[]),'<approval>','exec'),ns)
   result=asyncio.run(ns['activate_exam'](42,99,100));self.assertIsNone(result)
   self.assertFalse(any(sql.lstrip().startswith('UPDATE ') for sql,_ in cur.calls))
 def test_parent_keeps_fixed_deadline(self):
  for subject in ('arabic',):
   source=(Path(__file__).parent/'database.py').read_text();deadline=NOW+timedelta(hours=3);start=NOW-timedelta(hours=21)
   task={'id':42,'school_review_id':7,'exam_duration_hours':24,'deadline':deadline}
   review={'exam_deleted':False,'exam_manual_closed':False,'exam_opens_at':start,'exam_closes_at':deadline}
   cur=Cursor([{'user_id':99},task,review,task]);ns={'connect':lambda:Conn(cur),'run':run,'datetime_now':lambda cur:NOW,'timedelta':timedelta}
   exec(compile(ast.Module(body=[extract(source,'activate_exam')],type_ignores=[]),'<approval>','exec'),ns)
   asyncio.run(ns['activate_exam'](42,99,100))
   updates=[params for sql,params in cur.calls if 'UPDATE' in sql and 'SET exam_pending_activation' in sql]
   self.assertEqual(updates[0][0],deadline);self.assertEqual(updates[0][1],start)
if __name__=='__main__':unittest.main()
