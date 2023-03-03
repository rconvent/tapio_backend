from django.test import TestCase
from tapio.models import *

# Create your tests here.


class TapioTest(TestCase):

    def testReport(self):  
        report  = Report.objects.first()
        if report :
            deltas = report.scenario_delta
            delta_scenario_1 = deltas.get("scenario_1", {}).get("delta", 0)
            delta_scenario_2 = deltas.get("scenario_2", {}).get("delta", 0)


            self.assertAlmostEqual(delta_scenario_1, 3996800)
            self.assertAlmostEqual(delta_scenario_2, 3989600)

            # change report year to see that we do not take into intial total emission
            report.year = 2026
            report.save()
            deltas = report.scenario_delta
            delta_scenario_1 = deltas.get("scenario_1", {}).get("delta", 0)
            delta_scenario_2 = deltas.get("scenario_2", {}).get("delta", 0)

            self.assertAlmostEqual(delta_scenario_1, 996780)
            self.assertAlmostEqual(delta_scenario_2, 989580)

        else : 
            self.assertEqual(1, 0)



