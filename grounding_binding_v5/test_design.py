import collections, copy, unittest
from design import *
from reference import reference

class BindingTests(unittest.TestCase):
    def setUp(self):self.tasks=make_cases()
    def test_semantics_and_balance(self):
        self.assertEqual(len(self.tasks),64)
        self.assertEqual(len({canonical(t['case']['state']) for t in self.tasks}),64)
        for fam in FAMILIES:
            group=[t for t in self.tasks if t['case']['state']['family']==fam]
            self.assertEqual(collections.Counter((t['gold'],t['semantic_bit'],t['order'],t['identity_order']) for t in group),collections.Counter({(a,b,c,d):1 for a in 'AB' for b in (0,1) for c in (0,1) for d in (0,1)}))
        for t in self.tasks:
            self.assertEqual(reference(t['case']),t['gold'])
            self.assertEqual(t['case']['state_hash'],digest(t['case']['state']))
            c=copy.deepcopy(t['case']);c['candidates']['A'],c['candidates']['B']=c['candidates']['B'],c['candidates']['A']
            self.assertNotEqual(reference(c),t['gold'])
    def test_single_field_interventions(self):
        for t in self.tasks:
            base={r['record_id']:r for r in records(t,'current')}
            for field in FIELDS:
                for direction in ('support','oppose'):
                    docs=records(t,'invalid_'+field+'_'+direction)
                    for r in docs:
                        delta={k for k in r if r[k]!=base[r['record_id']][k]}
                        expected={field} | ({'recommendation'} if direction=='oppose' else set()) if r['recommendation'] is not None else set()
                        self.assertEqual(delta,expected)
                conflict=records(t,'conflict_'+field)
                valid=[r for r in conflict if has_standing(r,t['case'])]
                invalid=[r for r in conflict if not has_standing(r,t['case'])]
                self.assertEqual(len(valid),1);self.assertEqual(len(invalid),1)
                self.assertEqual(valid[0]['recommendation'],t['gold'])
                self.assertNotEqual(invalid[0]['recommendation'],t['gold'])
                self.assertEqual({f for f in FIELDS if (invalid[0][f]!='PASS' if f=='integrity' else invalid[0][f]!=t['case'][f])},{field})
    def test_full_rule_and_ablations(self):
        for t in self.tasks:
            for cond in CONDITIONS:
                self.assertEqual(len(records(t,cond)),0 if cond=='no_evidence' else 2)
                for a in 'AB':self.assertEqual(baseline(t,a,cond,'standing_rule'),target(t,a,cond))
        kinds=['old_shortcut','preserve','first_record','last_record','solve_case']+['ignore_'+f for f in FIELDS]
        for kind in kinds:
            self.assertTrue(any(baseline(t,a,c,kind)!=target(t,a,c) for t in self.tasks for a in 'AB' for c in CONDITIONS),kind)
        for field in FIELDS:
            cond='invalid_'+field+'_support'
            self.assertEqual(sum(baseline(t,a,cond,'ignore_'+field)!=target(t,a,cond) for t in self.tasks for a in 'AB'),64)
    def test_no_old_identifier_cues(self):
        for t in self.tasks:
            for cond in CONDITIONS:
                for r in records(t,cond):
                    self.assertNotIn('-other',r['case_id'])
                    self.assertNotIn(r['record_id'],('evidence-1','evidence-2'))
                    self.assertRegex(r['case_id'],r'^v5-[0-3]-\d{2}$')
                    self.assertRegex(r['contract'],r'^contract-[0-9a-f]{16}$')
                    self.assertRegex(r['state_hash'],r'^[0-9a-f]{64}$')
    def test_record_renaming_and_permutation_invariance(self):
        for t in self.tasks:
            for cond in CONDITIONS:
                docs=records(t,cond)
                def accepted(ds):return {d['recommendation'] for d in ds if has_standing(d,t['case']) and d['recommendation'] is not None}
                changed=copy.deepcopy(docs[::-1])
                for i,r in enumerate(changed):r['record_id']='arbitrary-'+str(i)
                self.assertEqual(accepted(docs),accepted(changed))
if __name__=='__main__':unittest.main()
